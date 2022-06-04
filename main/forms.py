from django import forms
from .models import Bid, Purchase, Sell, NFT, NFTCollection, Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["user", "wallet_address", "wallet_private_key"]
        widgets = {
            "wallet_address": forms.TextInput(attrs={"class": "form-control"}),
            "wallet_private_key": forms.TextInput(attrs={"class": "form-control"}),
        }


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["bid_price"]


class SellForm(forms.ModelForm):
    class Meta:
        model = Sell
        fields = ["sale_ends", "min_bid_price"]


class NFTCollectionForm(forms.ModelForm):
    class Meta:
        model = NFTCollection
        fields = ["name", "blockchain", "metadata_dir_url", "description", "metadata_file"]


class NFTForm(forms.ModelForm):
    class Meta:
        model = NFT
        fields = ["nft_name", "metadata_uri", "blockchain", "description"]


class FileFieldForm(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={"multiple": True}))
