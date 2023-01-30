# Generated by Django 4.1.5 on 2023-01-28 14:42

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import taggit.managers
import uuid
import web3_auth.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("taggit", "0005_auto_20220424_2025"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("profile_image_url", models.URLField(blank=True, null=True)),
                ("ethereum_wallet_address", models.CharField(max_length=42)),
                (
                    "ethereum_wallet_private_key",
                    models.CharField(blank=True, max_length=64, null=True),
                ),
                (
                    "pinata_ipfs_api_key",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                (
                    "pinata_ipfs_api_secret",
                    models.CharField(blank=True, max_length=64, null=True),
                ),
                (
                    "infura_ipfs_project_id",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "infura_ipfs_secret_key",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "infura_ethereum_project_id",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "infura_ethereum_secret_key",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "aws_s3_bucket",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "aws_s3_region",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "aws_access_key_id_value",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "aws_secret_access_key_value",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "etherscan_token",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "ordering": ["-id"],
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Asset",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "asset_type",
                    models.CharField(
                        choices=[
                            ("image", "Image File"),
                            ("audio", "Audio File"),
                            ("video", "Video File"),
                            ("file", "Generic File"),
                            ("other", "Other Type"),
                        ],
                        default="image",
                        max_length=32,
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                (
                    "token_id",
                    models.IntegerField(default=web3_auth.models.random_token),
                ),
                ("uri_asset", models.URLField()),
                ("uri_metadata", models.URLField()),
                ("uri_preview", models.URLField()),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "likes",
                    models.ManyToManyField(
                        related_name="likes", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
            options={
                "ordering": ["-id"],
            },
        ),
        migrations.CreateModel(
            name="Auction",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "network",
                    models.CharField(
                        choices=[
                            ("matic_main", "matic_main"),
                            ("mumbai", "mumbai"),
                            ("goerli", "goerli"),
                        ],
                        default="goerli",
                        max_length=32,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                (
                    "contract_address",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "datetime_start",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "datetime_end",
                    models.DateTimeField(default=web3_auth.models.now_plus_30),
                ),
                ("bid_start_value", models.FloatField()),
                ("bid_current_value", models.FloatField(default=0)),
                ("uri_preview", models.URLField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("unsold", "Unsold"), ("sold", "Sold")],
                        default="unsold",
                        max_length=32,
                    ),
                ),
            ],
            options={
                "ordering": ["-id"],
            },
        ),
        migrations.CreateModel(
            name="Bid",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("bid_time", models.DateTimeField(auto_now_add=True)),
                ("value", models.FloatField()),
                (
                    "status",
                    models.CharField(
                        choices=[("unsold", "Unsold"), ("sold", "Sold")],
                        default="unsold",
                        max_length=32,
                    ),
                ),
                (
                    "auction",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="web3_auth.auction",
                    ),
                ),
                (
                    "buyer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-value"],
            },
        ),
        migrations.CreateModel(
            name="Collection",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "collection_type",
                    models.CharField(
                        choices=[
                            ("image", "Image File"),
                            ("audio", "Audio Files"),
                            ("video", "Video Files"),
                            ("file", "Generic Files"),
                            ("misc", "Misc. Types"),
                        ],
                        default="image",
                        max_length=32,
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                (
                    "token_id",
                    models.IntegerField(default=web3_auth.models.random_token),
                ),
                ("uri_metadata", models.URLField()),
                ("uri_preview", models.URLField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("unsold", "Unsold"), ("sold", "Sold")],
                        default="unsold",
                        max_length=32,
                    ),
                ),
                (
                    "assets",
                    models.ManyToManyField(related_name="assets", to="web3_auth.asset"),
                ),
                (
                    "seller",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
            options={
                "ordering": ["-id"],
            },
        ),
        migrations.CreateModel(
            name="Raffle",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("contract_address", models.CharField(max_length=100)),
                (
                    "network",
                    models.CharField(
                        choices=[
                            ("matic_main", "matic_main"),
                            ("mumbai", "mumbai"),
                            ("goerli", "goerli"),
                        ],
                        default="goerli",
                        max_length=32,
                    ),
                ),
                (
                    "datetime_start",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "datetime_end",
                    models.DateTimeField(default=web3_auth.models.now_plus_30),
                ),
                ("price_entry", models.FloatField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("not_won", "raffle ended without winners"),
                            ("won", "raffle ended with winners"),
                        ],
                        default="scheduled",
                        max_length=32,
                    ),
                ),
                (
                    "collection",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="web3_auth.collection",
                    ),
                ),
                (
                    "participants",
                    models.ManyToManyField(
                        related_name="participants", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "winner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-id"],
            },
        ),
        migrations.CreateModel(
            name="Purchase",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("tx_hash", models.CharField(blank=True, max_length=200)),
                ("tx_token", models.CharField(blank=True, max_length=200)),
                ("purchase_time", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("aborted", "Purchase Aborted"),
                            ("running", "Puchase in Progress"),
                            ("complete", "Purchase Complete"),
                        ],
                        default="running",
                        max_length=32,
                    ),
                ),
                (
                    "bid",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="web3_auth.bid"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="auction",
            name="collections",
            field=models.ManyToManyField(
                related_name="collections", to="web3_auth.collection"
            ),
        ),
        migrations.AddField(
            model_name="auction",
            name="seller",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="auction",
            name="tags",
            field=taggit.managers.TaggableManager(
                help_text="A comma-separated list of tags.",
                through="taggit.TaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
    ]
