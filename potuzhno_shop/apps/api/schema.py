import graphene
from graphql import GraphQLError
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
# from graphene_django.debug import DjangoDebug
from django.db import transaction
from django.contrib.auth.models import User

from apps.api.filters import ProductFilter
from apps.shop.forms import ReviewForm
from apps.shop.models import Product, Brand, Category, Review


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class BrandType(DjangoObjectType):
    class Meta:
        model = Brand
        fields = ("id", "name", "slug")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = (
            "id", "name", "slug", "description", "price", "category", "brand",
            "audience", "is_featured", "created_at"
        )


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("username", "first_name", "email")


class ReviewType(DjangoObjectType):
    class Meta:
        model = Review
        fields = ("id", "rating", "text", "user", "product")

    # async def resolve_user(self, info):
    #     return await info.context.loaders.user_by_id.load(self.user_id)


class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (relay.Node,)          # ← обов'язково
        fields = (
            "id", "name", "slug", "description", "price",
            "category", "brand", "audience", "is_featured", "created_at",
            "reviews"
        )

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.with_rating().select_related("category", "brand")


class Query(graphene.ObjectType):
    # debug = graphene.Field(DjangoDebug, name="_debug")
    all_products = graphene.List(ProductType)
    product = graphene.Field(ProductType, slug=graphene.String(required=True) )
    all_categories = graphene.List(CategoryType)
    all_reviews = graphene.List(ReviewType)
    products = DjangoFilterConnectionField(ProductNode, filterset_class=ProductFilter)

    def resolve_all_products(self, info):
        return (
            Product.objects.filter(is_active=True)
            .select_related("category", "brand")
            .prefetch_related("reviews__users", "sizes")
        )
        # raise GraphQLError("Не можна!", extensions={
        #     "error1": "text error1",
        #     "error2": "text error2",
        #     "error3": "text error3",
        # })

    def resolve_product(self, info, slug):
        return Product.objects.get(slug=slug)

    def resolve_all_categories(self, info):
        return Category.objects.all()

    def resolve_all_reviews(self, info):
        return Review.objects.all()


class AddToFavourite(graphene.Mutation):
    class Arguments:
        slug = graphene.String(required=True)

    ok = graphene.Boolean()
    product = graphene.Field(ProductType)

    @staticmethod
    def mutate(root, info, slug):
        user = info.context.user

        if not user.is_authenticated:
            raise GraphQLError("Потрібно увійти в акаунт, щоб керувати улюбленими товарами")

        product = Product.objects.filter(slug=slug).first()
        if product is None:
            raise GraphQLError("Товар не знайдено")

        user.profile.favourites.add(product)

        return AddToFavourite(
            ok=True,
            product=product
        )


class RemoveFromFavourite(graphene.Mutation):
    class Arguments:
        slug = graphene.String(required=True)

    ok = graphene.Boolean()
    product = graphene.Field(ProductType)

    @staticmethod
    def mutate(root, info, slug):
        user = info.context.user

        if not user.is_authenticated:
            raise GraphQLError("Потрібно увійти в акаунт, щоб керувати улюбленими товарами")

        product = Product.objects.filter(slug=slug).first()
        if product is None:
            raise GraphQLError("Товар не знайдено")

        user.profile.favourites.remove(product)

        return AddToFavourite(
            ok=True,
            product=product
        )


class AddReview(graphene.Mutation):
    class Arguments:
        product_slug = graphene.String(required=True)
        rating = graphene.Int(required=True)
        text = graphene.String()

    ok = graphene.Boolean()
    review = graphene.Field(ReviewType)
    errors = graphene.List(graphene.String)

    @staticmethod
    @transaction.atomic
    def mutate(root, info, product_slug, rating, text=""):
        user = info.context.user

        if not user.is_authenticated:
            raise GraphQLError("Потрібно увійти в акаунт, щоб створити відгук")

        product = Product.objects.filter(slug=product_slug).first()
        if product is None:
            raise GraphQLError("Продукту не існує")

        form = ReviewForm({"rating": rating, "text": text})

        if not form.is_valid():
            return AddReview(
                ok=False,
                errors=[msgs[0] for field, msgs in form.errors.items()]
            )

        review = form.save(commit=False)
        review.user = user
        review.product = product
        review.save()

        return AddReview(
            ok=True,
            review=review
        )

class Mutation(graphene.ObjectType):
    add_to_favourite = AddToFavourite.Field()
    remove_from_favourite = RemoveFromFavourite.Field()
    add_review = AddReview.Field()



schema = graphene.Schema(query=Query, mutation=Mutation)