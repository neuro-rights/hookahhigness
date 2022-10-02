from django.db import models
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User, AbstractUser
from django.core.signals import request_finished
from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

from datetime import datetime, timedelta
import random
import uuid


def random_token():
    return int(random.randint(10000, 99999))


def now_plus_30():
    return datetime.now() + timedelta(days = 30)


def model_decorator(model):

    def get_all_fields(self):
        """Returns a list of all field names on the instance."""
        fields = []
        for f in self._meta.fields:

            fname = f.name        
            # resolve picklists/choices, with get_xyz_display() function
            get_choice = 'get_'+fname+'_display'
            if hasattr(self, get_choice):
                value = getattr(self, get_choice)()
            else:
                try:
                    value = getattr(self, fname)
                except AttributeError:
                    value = None

            # only display fields with values and skip some fields entirely
            if f.editable:

                fields.append(
                  {
                   'label':f.verbose_name, 
                   'name':f.name, 
                   'value':value,
                  }
                )

        return fields

    model.get_all_fields = get_all_fields
    return model


class User(AbstractUser):
    pass
    #
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    #
    profile_image_url = models.URLField(max_length=200, blank=True, null=True)
    # WALLET
    ethereum_wallet_address = models.CharField(max_length=42)
    ethereum_wallet_private_key = models.CharField(
        max_length=64, blank=True, null=True
    )
    # PINATA
    pinata_ipfs_api_key = models.CharField(max_length=20, blank=True, null=True)
    pinata_ipfs_api_secret = models.CharField(
        max_length=64, blank=True, null=True
    )
    # INFURA IPFS
    infura_ipfs_project_id = models.CharField(
        max_length=100, blank=True, null=True
    )
    infura_ipfs_secret_key = models.CharField(
        max_length=100, blank=True, null=True
    )
    # INFURA ETHEREUM
    infura_ethereum_project_id = models.CharField(
        max_length=100, blank=True, null=True
    )
    infura_ethereum_secret_key = models.CharField(
        max_length=100, blank=True, null=True
    )
    # AWS S3
    aws_s3_bucket = models.CharField(max_length=100, blank=True, null=True)
    aws_s3_region = models.CharField(max_length=100, blank=True, null=True)
    aws_access_key_id_value = models.CharField(
        max_length=100, blank=True, null=True
    )
    aws_secret_access_key_value = models.CharField(
        max_length=100, blank=True, null=True
    )
    #
    etherscan_token = models.CharField(max_length=100, blank=True, null=True)
    #
    class Meta:
        ordering = ["-id"]
    #
    def __str__(self):
        return self.username


@model_decorator
class Nft(models.Model):
    #
    NFT_TYPES = (
        ("image", "Image File"),
        ("audio", "Audio File"),
        ("video", "Video File"),
        ("file", "Generic File"),
        ("other", "Other Type"),
    )
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    nft_type = models.CharField(
        max_length=32,
        choices=NFT_TYPES,
        default="2d",
    )
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    #
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    likes = models.ManyToManyField(User, related_name="likes")
    token_id = models.IntegerField(default=random_token)
    #
    uri_asset = models.URLField(max_length=200)
    uri_metadata = models.URLField(max_length=200)
    uri_preview = models.URLField(max_length=200)

    class Meta:
        ordering = ["-id"]
    #
    @property
    def total_likes(self):
        return self.likes.count()
    #
    def __str__(self):
        return self.name
    #
    def get_asset_uri(self):
        return self.uri_asset
    #
    def get_absolute_url(self):
        return reverse("nft_detail", kwargs={"nft_uuid": self.uuid})


@model_decorator
class Asset(models.Model):
    #
    ASSET_TYPES = (
        ("image", "Image File"),
        ("audio", "Audio Files"),
        ("video", "Video Files"),
        ("file", "Generic Files"),
        ("misc", "Misc. Types"),
    )
    #
    ASSET_STATUS = (
        ("unsold", "Unsold"),
        ("sold", "Sold"),
    )
    #
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    asset_type = models.CharField(
        max_length=32, choices=ASSET_TYPES, default="2d"
    )
    #
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    nfts = models.ManyToManyField(Nft, related_name="nfts")
    #
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    token_id = models.IntegerField(default=random_token)
    #
    metadata_uri = models.URLField(max_length=200)
    uri_preview = models.URLField(max_length=200, blank=True, null=True)
    #
    status = models.CharField(
        max_length=32, choices=ASSET_STATUS, default="unsold"
    )

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.name

    @property
    def get_random_nft(self):
        return self.nfts.order_by("?").first()

    @property
    def get_random_nfts(self):
        return self.nfts.all()[:18][::-1]

    @property
    def num_nfts(self):
        return self.nfts.all().count()

    @property
    def total_likes(self):
        return self.nfts.aggregate(Count("likes"))["likes__count"]

    #
    def get_absolute_url(self):
        return reverse("asset_detail", kwargs={"asset_uuid": self.uuid})


@model_decorator
class Auction(models.Model):
    #
    AUCTION_STATUS = (
        ("unsold", "Unsold"),
        ("sold", "Sold"),
    )
    #
    BLOCKCHAIN_TYPES = (
        ("matic_main", "matic_main"),
        ("mumbai", "mumbai"),
        ("goerli", "goerli"),
        ("rinkeby", "rinkeby"),
    )
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    #
    assets = models.ManyToManyField(Asset, related_name="assets")
    network = models.CharField(
        max_length=32, choices=BLOCKCHAIN_TYPES, default="rinkeby"
    )
    description = models.TextField(blank=True)
    contract_address = models.CharField(max_length=100, blank=True, null=True)
    #
    datetime_start = models.DateTimeField(default=now)
    datetime_end = models.DateTimeField(default=now_plus_30)
    #
    bid_start_value = models.FloatField()
    bid_current_value = models.FloatField(default=0)
    #
    uri_preview = models.URLField(max_length=200, blank=True, null=True)

    status = models.CharField(
        max_length=32,
        choices=AUCTION_STATUS,
        default="unsold",
    )

    class Meta:
        ordering = ["-id"]

    def bids(self):
        return Bid.objects.filter(auction=self)

    @property
    def total_bids(self):
        return self.bids.count()

    def get_absolute_url(self):
        return reverse("auction_detail", kwargs={"auction_uuid": self.uuid})


@model_decorator
class Bid(models.Model):
    """ """

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, blank=True, null=True, on_delete=models.CASCADE)
    bid_time = models.DateTimeField(auto_now_add=True, editable=False)
    value = models.FloatField()

    def __str__(self):
        return f"{self.get_value_display()} on {self.bid_time}"

    class Meta:
        ordering = ["-value"]
    
    def get_absolute_url(self):
        return reverse("bid_detail", kwargs={"bid_uuid": self.uuid})


@model_decorator
class Raffle(models.Model):
    #
    RAFFLE_STATUS = (
        ("not_won", "raffle ended without winners"),
        ("won", "raffle ended with winners"),
    )
    #
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True, blank=True)
    #
    participants = models.ManyToManyField(User, related_name="participants")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    #
    datetime_start = models.DateTimeField(default=now)
    datetime_end = models.DateTimeField(default=now_plus_30)
    #
    price_entry = models.FloatField()
    #
    status = models.CharField(
        max_length=32,
        choices=RAFFLE_STATUS,
        default="scheduled",
    )

    class Meta:
        ordering = ["-id"]
    
    def get_absolute_url(self):
        return reverse("raffle_detail", kwargs={"raffle_uuid": self.uuid})


@model_decorator
class Purchase(models.Model):
    """ """

    PURCHASE_STATUS = (
        ("aborted", "Purchase Aborted"),
        ("running", "Puchase in Progress"),
        ("complete", "Purchase Complete"),
    )

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    tx_hash = models.CharField(blank=True, max_length=200)
    tx_token = models.CharField(blank=True, max_length=200)
    purchase_time = models.DateTimeField(auto_now_add=True, editable=False)
    status = models.CharField(
        max_length=32,
        choices=PURCHASE_STATUS,
        default="running",
    )
    
    def get_absolute_url(self):
        return reverse("purchase_detail", kwargs={"purchase_uuid": self.uuid})

