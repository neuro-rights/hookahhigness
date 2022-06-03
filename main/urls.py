from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("accounts/signup/", views.signup, name="signup"),
    path("accounts/settings/", views.settings, name="settings"),
    path("accounts/profile/", views.settings, name="profile"),
    path("collections/create/", views.NFTCollectionCreate.as_view(), name="collection_create"),
    path("collections/own/", views.collection_own, name="collection_own"),
    path("collections/all/", views.NFTCollectionList.as_view(), name="collection_list"),
    path("collections/<int:collection_id>/", views.collection_detail, name="collection_detail"),
    path("collections/<int:pk>/edit/", views.NFTCollectionEdit.as_view(), name="collection_edit"),
    path("collections/<int:collection_id>/add_nfts/", views.add_nfts, name="add_nfts"),
    path("collections/<int:collection_id>/add_collection_metadata/", views.add_nfts, name="add_collection_metadata"),
    path("collections/<int:pk>/delete/", views.NFTCollectionDelete.as_view(), name="collection_delete"),
    path("nfts/create/", views.NFTCreate.as_view(), name="nft_create"),
    path("nfts/<int:nft_id>/", views.nft_detail, name="nft_detail"),
    path("nfts/own/", views.nft_own, name="nft_own"),
    path("nfts/all/", views.NFTList.as_view(), name="nft_list"),
    path("nfts/<int:pk>/edit/", views.NFTEdit.as_view(), name="nft_edit"),
    path("nfts/<int:nft_id>/add_photo/", views.add_photo, name="add_photo"),
    path("nfts/<int:pk>/delete/", views.NFTDelete.as_view(), name="nft_delete"),
    path("nfts/<int:nft_id>/add_bid/", views.add_bid, name="add_bid"),
    path("nfts/search_result/", views.search_result, name="search_result"),
    path("nfts/<int:nft_id>/add_sell/", views.sell, name="sell"),
    path("nfts/for_sale", views.all_for_sale, name="for_sale"),
    path("like/<int:pk>", views.likeview, name="like_nft"),
    path("bids/<int:bid_id>/accept_bid/", views.accept_bid, name="accept_bid"),
    path("bids/<int:bid_id>/reject_bid/", views.reject_bid, name="reject_bid"),
    # path('ajax/transaction_progress', views.transaction_progress, name='transaction_progress'),
    # path('ajax/upload_progress', views.upload_progress, name='upload_progress'),
]
