from django import forms
from django.contrib.auth.forms import UserCreationForm
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from .models import User, Nft, Asset, Raffle, Auction, Bid, Purchase

from datetime import datetime, timedelta
from libgravatar import Gravatar


class UserCreateForm(forms.ModelForm):
    """
    A form for creating new users.
    Includes all the required fields, plus a repeated password.
    """

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update(
                {
                    "class": "input-field",
                    "placeholder": "{}".format(field)
                    .replace("_", " ")
                    .capitalize(),
                }
            )
        #
        self.fields["password1"].widget.attrs[
            "placeholder"
        ] = "please enter your password"
        self.fields["password2"].widget.attrs[
            "placeholder"
        ] = "confirm your password"
        self.fields["username"].widget.attrs["placeholder"] = "username"
        self.fields["username"].required = True
        self.fields["email"].widget.attrs["placeholder"] = "email@domain.tld"
        self.fields["email"].required = True

        if self.instance.pk:
            self.fields["username"].required = False
            self.fields["username"].widget.attrs["readonly"] = True
            self.fields["email"].required = False
            self.fields["email"].widget.attrs["readonly"] = True

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        self.date_joined = datetime.today()
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.profile_image_url = Gravatar(user.email).get_image()
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ["username", "email"]


class UserEditForm(forms.ModelForm):
    """ """

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update(
                {
                    "class": "input-field",
                    "placeholder": "{}".format(field)
                    .replace("_", " ")
                    .capitalize(),
                }
            )
        #
        self.fields["profile_image_url"].widget.attrs[
            "placeholder"
        ] = "https://domain.tld/"
        self.fields["ethereum_wallet_address"].widget.attrs[
            "placeholder"
        ] = "0x 40 hex characters"
        self.fields["ethereum_wallet_private_key"].widget.attrs[
            "placeholder"
        ] = "64 hex characters"
        self.fields["pinata_ipfs_api_key"].widget.attrs[
            "placeholder"
        ] = "20 hex characters"
        self.fields["pinata_ipfs_api_secret"].widget.attrs[
            "placeholder"
        ] = "64 hex characters"
        self.fields["infura_ethereum_project_id"].widget.attrs[
            "placeholder"
        ] = "27 characters"
        self.fields["infura_ethereum_secret_key"].widget.attrs[
            "placeholder"
        ] = "32 hex characters"
        self.fields["aws_s3_bucket"].widget.attrs[
            "placeholder"
        ] = "your aws s3 bucket name"
        self.fields["aws_s3_region"].widget.attrs[
            "placeholder"
        ] = "your aws s3 region"

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = [
            "profile_image_url",
            "ethereum_wallet_address",
            "ethereum_wallet_private_key",
            "pinata_ipfs_api_key",
            "pinata_ipfs_api_secret",
            "infura_ipfs_project_id",
            "infura_ipfs_secret_key",
            "infura_ethereum_project_id",
            "infura_ethereum_secret_key",
            "aws_s3_bucket",
            "aws_s3_region",
            "aws_access_key_id_value",
            "aws_secret_access_key_value",
            "etherscan_token",
        ]


class NftForm(forms.ModelForm):
    """ """

    def __init__(self, request, *args, **kwargs):
        """Grants access to the request object so that only members of the current user
        are given as options"""
        super(NftForm, self).__init__(*args, **kwargs)
        self.request = request

    def save(self, commit=True):
        """ """
        instance = super().save(commit=False)
        instance.creator = self.request.user
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        """ """

        model = Nft
        fields = [
            "name",
            "description",
            "nft_type",
        ]


class AssetForm(forms.ModelForm):
    """ """
    def __init__(self, request, *args, **kwargs):
        """Grants access to the request object so that only members of the current user
        are given as options"""
        super(AssetForm, self).__init__(*args, **kwargs)
        self.request = request
        """
        self.fields["nfts"].queryset = Nft.objects.filter(
            creator=self.request.user
        )
        """

    def save(self, commit=True):
        """ """
        instance = super().save(commit=False)
        instance.seller = self.request.user
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        """ """

        model = Asset
        fields = [
            "asset_type",
            #"seller",
            #"nfts",
            "name",
            "description",
            #"token_id",
            #"metadata_uri",
            #"status"
        ]


class AssetFromFilesForm(forms.ModelForm):
    """ """

    image_files = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True})
    )

    def __init__(self, request, *args, **kwargs):
        """Grants access to the request object so that only members of the current user
        are given as options"""
        super(AssetFromFilesForm, self).__init__(*args, **kwargs)
        self.request = request

    def save(self, commit=True):
        """ """
        instance = super().save(commit=False)
        instance.seller = self.request.user
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        """ """

        model = Asset
        fields = [
        ]


class AssetFromNftsForm(forms.ModelForm):
    """ """

    nfts = forms.ModelMultipleChoiceField(
        queryset=None, widget=forms.SelectMultiple
    )

    def __init__(self, request, *args, **kwargs):
        """Grants access to the request object so that only members of the current user
        are given as options"""
        super(AssetFromNftsForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields["nfts"].queryset = Nft.objects.filter(
            creator=self.request.user
        )

    def save(self, commit=True):
        """ """
        instance = super().save(commit=False)
        instance.seller = self.request.user
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        """ """

        model = Asset
        fields = [
            "nfts",
        ]


class AssetFromMetadataURLForm(forms.ModelForm):
    """ """

    metadata_file = forms.FileField(widget=forms.ClearableFileInput())

    def __init__(self, request, *args, **kwargs):
        """Grants access to the request object so that only members of the current user
        are given as options"""
        super(AssetFromMetadataURLForm, self).__init__(*args, **kwargs)
        self.request = request

    def save(self, commit=True):
        """ """
        instance = super().save(commit=False)
        instance.seller = self.request.user
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        """ """

        model = Asset
        fields = [
            "metadata_uri",
        ]


class AuctionForm(forms.ModelForm):
    """ """

    assets = forms.ModelMultipleChoiceField(
        queryset=None, widget=forms.SelectMultiple
    )

    def __init__(self, request, *args, **kwargs):
        """Grants access to the request object so that only members of the current user
        are given as options"""
        super(AuctionForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields["assets"].queryset = Asset.objects.filter(
            seller=self.request.user
        )

    def save(self, commit=True):
        """ """
        instance = super().save(commit=False)
        instance.seller = self.request.user
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        """ """

        model = Auction
        fields = [
            "assets",
            "blockchain",
            "description",
            "datetime_start",
            "datetime_end",
            "bid_start_value",
            "status",
        ]
        widgets = {
            "datetime_start": DateTimePickerInput(),
            "datetime_end": DateTimePickerInput(),
        }


class BidForm(forms.ModelForm):
    """ """

    def __init__(self, request, *args, **kwargs):
        """Grants access to the request object so that only members of the current user
        are given as options"""
        super(BidForm, self).__init__(*args, **kwargs)
        self.request = request

    def save(self, commit=True):
        """ """
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
        return instance
    
    def is_valid(self):
 
        # run the parent validation first
        valid = super(BidForm, self).is_valid()
        # we're done now if not valid
        print(self._errors)
        return True

    class Meta:
        """ """
        model = Bid
        fields = ["value"]


class PurchaseForm(forms.ModelForm):
    """ """

    def __init__(self, request, *args, **kwargs):
        """Grants access to the request object so that only members of the current user
        are given as options"""
        super(PurchaseForm, self).__init__(*args, **kwargs)
        self.request = request

    def save(self, commit=True):
        """ """
        instance = super().save(commit=False)
        instance.seller = instance.bid.auction.seller
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        """ """

        model = Purchase
        fields = ["tx_hash", "tx_token", "status"]


class RaffleForm(forms.ModelForm):
    """ """

    asset = forms.ModelChoiceField(queryset=None, widget=forms.Select)

    def __init__(self, request, *args, **kwargs):
        """Grants access to the request object so that only members of the current user
        are given as options"""
        super(RaffleForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields["asset"].queryset = Asset.objects.filter(
            seller=self.request.user
        )

    class Meta:
        """ """

        model = Raffle
        fields = [
            "asset",
            "datetime_start",
            "datetime_end",
            "price_entry",
            "status",
        ]
        #
        widgets = {
            "datetime_start": DateTimePickerInput(),
            "datetime_end": DateTimePickerInput()
        }


class FileFieldForm(forms.Form):
    file_field = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True})
    )
