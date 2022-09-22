from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("help", views.home, name="help"),
    path('<str:room_name>/', views.room, name='room'),
    path("about", views.home, name="about"),
    path("accounts/signup/", views.signup, name="signup"),
    path("accounts/profile/", views.profile, name="profile"),
    path("accounts/followers/", views.profile, name="followers"),
    # NFTS
    path("nfts/ajax/", views.NftListJson.as_view(), name="ajax_datatable_nfts"),
    path("nfts/own/", views.nfts_own, name="nfts_own"),
    path("nfts/2d/", views.nfts_own_2d, name="nfts_own_2d"),
    path("nfts/3d/", views.nfts_own_3d, name="nfts_own_3d"),
    path("nfts/music/", views.nfts_own_music, name="nfts_own_music"),
    path("nfts/video/", views.nfts_own_video, name="nfts_own_video"),
    path("nfts/doc/", views.nfts_own_doc, name="nfts_own_doc"),
    path("nft/create/", views.NftCreate.as_view(), name="nft_create"),
    path("nft/search_result/", views.search_result, name="search_result"),
    path("nft/<uuid:nft_uuid>/", views.nft_detail, name="nft_detail"),
    path("nft/<uuid:nft_uuid>/delete/", views.NftDelete.as_view(), name="nft_delete"),
    path("nft/<uuid:nft_uuid>/edit/", views.NftEdit.as_view(), name="nft_edit"),
    # Auction NFT
    path("nft/<uuid:nft_uuid>/add_auction", views.nft_add_auction, name="nft_add_auction"),
    # Add File to NFT
    path("nft/<uuid:nft_uuid>/nft_add_file_to_s3", views.nft_add_file_to_s3, name="nft_add_file_to_s3"),
    # LIKES
    path("nft/<uuid:nft_uuid>/like", views.like_nft, name="like_nft"),
    # ASSETS
    path("assets/ajax/", views.AssetListJson.as_view(), name="ajax_datatable_assets"),
    path("assets/own/", views.assets_own, name="assets_own"),
    path("asset/create/", views.AssetCreate.as_view(), name="asset_create"),
    path("asset/create_from_files/", views.AssetFromFilesCreate.as_view(), name="asset_create_from_files"),
    path("asset/create_from_nfts/", views.AssetFromNftsCreate.as_view(), name="asset_create_from_nfts"),
    path("asset/create_from_metadata_url/", views.AssetFromMetadataURLCreate.as_view(), name="asset_create_from_metadata_url"),
    path("asset/<uuid:asset_uuid>/", views.asset_detail, name="asset_detail"),
    path("asset/<uuid:asset_uuid>/add_auction/", views.asset_add_auction, name="asset_add_auction"),
    path("asset/<uuid:asset_uuid>/add_nfts/", views.asset_add_nfts, name="asset_add_nfts"),
    path("asset/<uuid:asset_uuid>/add_raffle/", views.asset_add_raffle, name="asset_add_raffle"),
    path("asset/<uuid:asset_uuid>/add_asset_metadata/", views.asset_add_metadata, name="add_asset_metadata"),
    path("asset/<uuid:asset_uuid>/edit/", views.AssetEdit.as_view(), name="asset_edit"),
    path("asset/<uuid:asset_uuid>/delete/", views.AssetDelete.as_view(), name="asset_delete"),
    # LIKES
    path("asset/<uuid:asset_uuid>/like", views.like_asset, name="like_asset"),
    # RAFFLE
    path("raffles/ajax/", views.RaffleListJson.as_view(), name="ajax_datatable_raffles"),
    path("raffles/own/", views.raffles_own, name="raffles_own"),
    path("raffles/ended/", views.raffles_own_ended, name="raffles_own_ended"),
    path("raffles/running/", views.raffles_own_running, name="raffles_own_running"),
    path("raffles/scheduled/", views.raffles_own_scheduled, name="raffles_own_scheduled"),
    path("raffle/create/", views.RaffleCreate.as_view(), name="raffle_create"),
    path("raffle/<uuid:raffle_uuid>/", views.raffle_detail, name="raffle_detail"),
    path("raffle/<uuid:raffle_uuid>/add_assets/", views.raffle_add_assets, name="raffle_add_assets"),
    path("raffle/<uuid:raffle_uuid>/participants", views.raffle_list_participants, name="raffle_list_participants"),
    path("raffle/<uuid:raffle_uuid>/add_participants", views.raffle_add_participants, name="raffle_add_participants"),
    path("raffle/<uuid:raffle_uuid>/edit/", views.RaffleEdit.as_view(), name="raffle_edit"),
    path("raffle/<uuid:raffle_uuid>/delete/", views.RaffleDelete.as_view(), name="raffle_delete"),
    # AUCTIONS
    path("auction/create/", views.AuctionCreate.as_view(), name="auction_create"),
    path("auctions/scheduled/", views.auctions_own_scheduled, name="auctions_own_scheduled"),
    path("auctions/running/", views.auctions_own_running, name="auctions_own_running"),
    path("auctions/ended/", views.auctions_own_ended, name="auctions_own_ended"),
    path("auctions/ajax/scheduled/", views.AuctionOwnScheduledListJson.as_view(), name="ajax_datatable_auctions_scheduled"),
    path("auctions/ajax/running/", views.AuctionOwnRunningListJson.as_view(), name="ajax_datatable_auctions_running"),
    path("auctions/ajax/ended/", views.AuctionOwnEndedListJson.as_view(), name="ajax_datatable_auctions_ended"),
    path("auction/<uuid:auction_uuid>/", views.auction_detail, name="auction_detail"),
    path("auction/<uuid:auction_uuid>/edit/", views.AuctionEdit.as_view(), name="auction_edit"),
    path("auction/<uuid:auction_uuid>/delete/", views.AuctionDelete.as_view(), name="auction_delete"),
    path("auction/<uuid:auction_uuid>/add_assets/", views.auction_add_assets, name="auction_add_assets"),
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
