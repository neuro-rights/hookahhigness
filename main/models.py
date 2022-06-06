from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.signals import request_finished
from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver

#
import random
import datetime


def random_token():
    return int(random.randint(10000, 99999))


class NFT(models.Model):
    #
    id = models.AutoField(primary_key=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name="likes")
    #
    nft_name = models.CharField(max_length=50)
    token_id = models.IntegerField(default=random_token)
    metadata_uri = models.URLField(max_length=200)
    blockchain = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    #
    def total_likes(self):
        return self.likes.count()
        form.instance.user = self.request.user
        return super().form_valid(form)

    #
    def __str__(self):
        return self.nft_name

    #
    def get_absolute_url(self):
        return reverse("nft_detail", kwargs={"nft_id": self.id})


class NFTCollection(models.Model):
    #
    id = models.AutoField(primary_key=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    token_id = models.IntegerField(default=random_token)
    nfts = models.ManyToManyField(NFT, related_name="nfts")
    #
    name = models.CharField(max_length=50)
    blockchain = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    metadata_file = models.FileField(upload_to="collections")
    metadata_dir_url = models.URLField(max_length=200)
    #
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
        form.instance.user = self.request.user
        return super().form_valid(form)

    #
    def get_absolute_url(self):
        return reverse("collection_detail", kwargs={"collection_id": self.id})


class Bid(models.Model):
    #
    id = models.AutoField(primary_key=True)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    nft = models.ForeignKey(NFT, on_delete=models.CASCADE)
    #
    bid_time = models.DateTimeField(auto_now_add=True)
    bid_price = models.FloatField()
    #
    def __str__(self):
        return f"{self.get_bid_price_display()} on {self.date}"

    #
    class Meta:
        ordering = ("-bid_price",)


class Purchase(models.Model):
    #
    id = models.AutoField(primary_key=True)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    #
    tx_hash = models.CharField(max_length=200)
    sale_time = models.DateTimeField(auto_now_add=True)


class Sell(models.Model):
    #
    id = models.AutoField(primary_key=True)
    nft = models.ForeignKey(NFT, on_delete=models.CASCADE)
    #
    sale_ends = models.DateField()
    min_bid_price = models.FloatField()

    def total_bids(self):
        return self.nft.bid_set.count()


class Photo(models.Model):
    #
    url = models.CharField(max_length=200)
    nft = models.ForeignKey(NFT, on_delete=models.CASCADE)
    #
    def __str__(self):
        return f"Photo for nft_id: {self.nft_id} @{self.url}"


class Profile(models.Model):
    #
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #
    wallet_address = models.CharField(max_length=36, blank=True, null=True)
    wallet_private_key = models.CharField(max_length=64, blank=True, null=True)
    #
    def __str__(self):
        return self.wallet_address
