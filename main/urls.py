from django.urls import path
from . import views


urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("help", views.home, name="help"),
    path('<str:room_name>/', views.room, name='room'),
    path("about", views.home, name="about"),
    path("accounts/signup/", views.signup, name="signup"),
    path("accounts/profile/", views.profile, name="profile"),
    path("accounts/followers/", views.profile, name="followers"),
    # NFTS
    path("assets/ajax/", views.AssetListJson.as_view(), name="ajax_datatable_assets"),
    path("assets/own/", views.assets_own, name="assets_own"),
    path("assets/2d/", views.assets_own_2d, name="assets_own_2d"),
    path("assets/3d/", views.assets_own_3d, name="assets_own_3d"),
    path("assets/music/", views.assets_own_music, name="assets_own_music"),
    path("assets/video/", views.assets_own_video, name="assets_own_video"),
    path("assets/doc/", views.assets_own_doc, name="assets_own_doc"),
    path("asset/create/", views.AssetCreate.as_view(), name="asset_create"),
    path("asset/search_result/", views.search_result, name="search_result"),
    path("asset/<uuid:asset_uuid>/", views.asset_detail, name="asset_detail"),
    path("asset/<uuid:asset_uuid>/delete/", views.AssetDelete.as_view(), name="asset_delete"),
    path("asset/<uuid:asset_uuid>/edit/", views.AssetEdit.as_view(), name="asset_edit"),
    # Auction NFT
    path("asset/<uuid:asset_uuid>/add_auction", views.asset_add_auction, name="asset_add_auction"),
    # Add File to NFT
    path("asset/<uuid:asset_uuid>/asset_add_file_to_s3", views.asset_add_file_to_s3, name="asset_add_file_to_s3"),
    # LIKES
    path("asset/<uuid:asset_uuid>/like", views.like_asset, name="like_asset"),
    # ASSETS
    path("collections/ajax/", views.CollectionListJson.as_view(), name="ajax_datatable_collections"),
    path("collections/own/", views.collections_own, name="collections_own"),
    path("collection/create/", views.CollectionCreate.as_view(), name="collection_create"),
    path("collection/create_from_files/", views.CollectionFromFilesCreate.as_view(), name="collection_create_from_files"),
    path("collection/create_from_assets/", views.CollectionFromAssetsCreate.as_view(), name="collection_create_from_assets"),
    path("collection/create_from_metadata_url/", views.CollectionFromMetadataURLCreate.as_view(), name="collection_create_from_metadata_url"),
    path("collection/<uuid:collection_uuid>/", views.collection_detail, name="collection_detail"),
    path("collection/<uuid:collection_uuid>/add_auction/", views.collection_add_auction, name="collection_add_auction"),
    path("collection/<uuid:collection_uuid>/add_assets/", views.collection_add_assets, name="collection_add_assets"),
    path("collection/<uuid:collection_uuid>/collection_add_files_to_s3/", views.collection_add_files_to_s3, name="collection_add_files_to_s3"),
    path("collection/<uuid:collection_uuid>/add_raffle/", views.collection_add_raffle, name="collection_add_raffle"),
    path("collection/<uuid:collection_uuid>/add_collection_metadata/", views.collection_add_metadata, name="add_collection_metadata"),
    path("collection/<uuid:collection_uuid>/edit/", views.CollectionEdit.as_view(), name="collection_edit"),
    path("collection/<uuid:collection_uuid>/delete/", views.CollectionDelete.as_view(), name="collection_delete"),
    # LIKES
    path("collection/<uuid:collection_uuid>/like", views.like_collection, name="like_collection"),
    # RAFFLE
    path("raffles/scheduled/", views.raffles_own_scheduled, name="raffles_own_scheduled"),
    path("raffles/running/", views.raffles_own_running, name="raffles_own_running"),
    path("raffles/ended/", views.raffles_own_ended, name="raffles_own_ended"),
    path("raffles/ajax/scheduled/", views.RaffleOwnScheduledListJson.as_view(), name="ajax_datatable_raffles_scheduled"),
    path("raffles/ajax/running/", views.RaffleOwnRunningListJson.as_view(), name="ajax_datatable_raffles_running"),
    path("raffles/ajax/ended/", views.RaffleOwnEndedListJson.as_view(), name="ajax_datatable_raffles_ended"),
    path("raffle/create/", views.RaffleCreate.as_view(), name="raffle_create"),
    path("raffle/<uuid:raffle_uuid>/", views.raffle_detail, name="raffle_detail"),
    path("raffle/<uuid:raffle_uuid>/add_collections/", views.raffle_add_collections, name="raffle_add_collections"),
    path("raffle/<uuid:raffle_uuid>/participants", views.raffle_list_participants, name="raffle_list_participants"),
    path("raffle/<uuid:raffle_uuid>/add_participants", views.raffle_add_participants, name="raffle_add_participants"),
    path("raffle/<uuid:raffle_uuid>/edit/", views.RaffleEdit.as_view(), name="raffle_edit"),
    path("raffle/<uuid:raffle_uuid>/delete/", views.RaffleDelete.as_view(), name="raffle_delete"),
    # AUCTIONS
    path("auctions/scheduled/", views.auctions_own_scheduled, name="auctions_own_scheduled"),
    path("auctions/running/", views.auctions_own_running, name="auctions_own_running"),
    path("auctions/ended/", views.auctions_own_ended, name="auctions_own_ended"),
    path("auctions/ajax/scheduled/", views.AuctionOwnScheduledListJson.as_view(), name="ajax_datatable_auctions_scheduled"),
    path("auctions/ajax/running/", views.AuctionOwnRunningListJson.as_view(), name="ajax_datatable_auctions_running"),
    path("auctions/ajax/ended/", views.AuctionOwnEndedListJson.as_view(), name="ajax_datatable_auctions_ended"),
    path("auction/create/", views.AuctionCreate.as_view(), name="auction_create"),
    path("auction/<uuid:auction_uuid>/", views.auction_detail, name="auction_detail"),
    path("auction/<uuid:auction_uuid>/edit/", views.AuctionEdit.as_view(), name="auction_edit"),
    path("auction/<uuid:auction_uuid>/delete/", views.AuctionDelete.as_view(), name="auction_delete"),
    path("auction/<uuid:auction_uuid>/add_collections/", views.auction_add_collections, name="auction_add_collections"),
    path("auction/<uuid:auction_uuid>/add_bid/", views.auction_add_bid, name="auction_add_bid"),
    path("auction/<uuid:auction_uuid>/bids/", views.auction_bids, name="auction_bids"),
    # BIDS
    path("bids/made/", views.BidMadeList.as_view(), name="bids_made_list"),
    path("bids/received/", views.BidReceivedList.as_view(), name="bids_received_list"),
    path("bids/ajax/made/", views.BidMadeListJson.as_view(), name="ajax_datatable_bids_made"),
    path("bids/ajax/received/", views.BidReceivedListJson.as_view(), name="ajax_datatable_bids_received"),
    path("bid/<uuid:bid_uuid>/accept/", views.bid_accept, name="bid_accept"),
    # PURCHASES
    path("purchases/bought/", views.PurchaseBoughtList.as_view(), name="purchases_bought_list"),
    path("purchases/sold/", views.PurchaseSoldList.as_view(), name="purchases_sold_list"),
    path("purchases/ajax/bought/", views.PurchaseBoughtListJson.as_view(), name="ajax_datatable_purchases_bought"),
    path("purchases/ajax/sold/", views.PurchaseSoldListJson.as_view(), name="ajax_datatable_purchases_sold"),
    # OPENSEA
    path("opensea/", views.opensea, name="opensea"),
    path("tickets/", views.tickets, name="tickets"),
]
