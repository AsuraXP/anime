<?php 
require('./_config.php');
session_start();




$parts=parse_url($_SERVER['REQUEST_URI']); 
$page_url=explode('/', $parts['path']);
$url = $page_url[count($page_url)-1];
//$url = "naruto-episode-2";
$animeID = explode('-episode-', $url);

$animeID = $animeID[0];
$slug = explode('-', $animeID);
$dub = "";
if(end($slug) == 'dub'){
    $dub = "dub";
}
else{
    $dub = "sub";
};

$getEpisode = file_get_contents("$api/getEpisode/$url");
$getEpisode = json_decode($getEpisode, true);
if(isset($getEpisode['error'])){
    header('Location: /');
};



$pageID = $url;

$CurPageURL = $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'];  
$pageUrl = $CurPageURL;

//check for count
$query = mysqli_query($conn, "SELECT * FROM `pageview` WHERE pageID = '$pageID'"); 
$rows = mysqli_fetch_array($query); 
$counter = $rows['totalview']; 

$id = $rows['id']; 
if(empty($counter)) 
{
 $counter = 1;
 mysqli_query($conn,"INSERT INTO `pageview` (pageID,totalview,like_count,dislike_count,animeID) VALUES('$pageID','$counter','1','0','$animeID')"); 
 header('Location: //'.$pageUrl);
};



$anime = $getEpisode['anime_info'];
$EPISODE_NUMBER = $getEpisode['ep_num'];
$download = str_replace("Gogoanime", "$websiteTitle", $getEpisode['ep_download']);

$streamingID = $download;
$streamingID = parse_url($streamingID);
parse_str($streamingID['query'], $streamingPID);
$streamingID = $streamingPID['id'];
$animeTitle = $streamingPID['title'];

$getAnime = file_get_contents("$api/getAnime/$anime");
$getAnime = json_decode($getAnime, true);

$animeSearch = trim($anime,"-dub");


$api_url = "$api/getepisode/$id";

// Fetch the JSON response from the API and store it in $json2
$json2 = file_get_contents($api_url);

// Decode the JSON into an array
$data2 = json_decode($json2, true);

// Extract necessary information
$animeNameWithEP2 = $data2['animeNameWithEP'];

// Replace spaces with hyphens in the anime name
$animeNameWithEP2 = str_replace(' ', '-', $animeNameWithEP2);

$episodelist = $getAnime['episode_id'];
$firstEpID =  $episodelist[0];
$firstEpID = $firstEpID['episodeId'];


$ANIME_RELEASED = $getAnime['released'];
$ANIME_name = $getAnime['name'];
$ANIME_NAME = rtrim($getAnime['name']);
$ANIME_IMAGE = $getAnime['imageUrl'];
$ANIME_TYPE = $getAnime['type'];

//increase counters by 1 on page load
$counter = $counter+1;
mysqli_query($conn,"UPDATE `pageview` SET totalview ='$counter' WHERE pageID = '$pageID'");
$like_count = $rows['like_count']; 
$dislike_count = $rows['dislike_count']; 
$totalVotes = $like_count + $dislike_count;

if(isset($_COOKIE['userID'])){
    $userID = $_COOKIE['userID'];

    $user_history = mysqli_query($conn, "SELECT * FROM `user_history` WHERE (user_id,anime_id) = ('$userID', '$url')"); 
    $user_history = mysqli_fetch_assoc($user_history); 
    $user_history_anime_id = $user_history['anime_id'];
    $user_history_id = $user_history['id'];
    //echo  $user_history_id ;

    if(empty($user_history_anime_id)){
        mysqli_query($conn,"INSERT INTO `user_history` (user_id,anime_id,anime_title,anime_ep,anime_image,anime_release,dubOrSub,anime_type)
        VALUES('$userID','$url','$ANIME_name','$EPISODE_NUMBER','$ANIME_IMAGE','$ANIME_RELEASED','$dub','$ANIME_TYPE')"); 
    }elseif($user_history_anime_id == $url){
        mysqli_query($conn,"DELETE FROM `user_history` WHERE id = '$user_history_id'"); 
        mysqli_query($conn,"INSERT INTO `user_history` (user_id,anime_id,anime_title,anime_ep,anime_image,anime_release,dubOrSub,anime_type)
        VALUES('$userID','$url','$ANIME_name','$EPISODE_NUMBER','$ANIME_IMAGE','$ANIME_RELEASED','$dub','$ANIME_TYPE')"); 
    }
   
}
?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" itemscope="" itemtype="http://schema.org/WebPage" lang="en-US">

<head prefix="og: http://ogp.me/ns# fb: http://ogp.me/ns/fb# article: http://ogp.me/ns/article#">
  <meta http-equiv="content-type" content="text/html; charset=UTF-8">
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
  <link rel="shortcut icon" href="/favicon.ico">
  

    
  
  <title>Watch <?=$getEpisode['animeNameWithEP']?> on AnimeZia | Chromecast Available</title>
  <meta name="robots" content="index, follow" />
  <meta name="description" content="Watch <?=$getEpisode['animeNameWithEP']?> on Ryuk" />
  <meta itemprop="image" content="/logo.png" />
  <meta property="og:site_name" content="Ryuk" />
  <meta property="og:locale" content="en_US" />
  <meta property="og:type" content="website" />
  <meta property="og:image" content="/logo.png" />
  <meta name="keywords" content="crunchyroll,9anime,gogoanime,aniwatch,animesuge">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.4.1/css/bootstrap.min.css"
      type="text/css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta2/css/all.min.css"
      type="text/css">
  <link rel="shortcut icon" href="<?=$websiteUrl?>/favicon.ico?v=<?=$version?>?v=<?=$version?>" type="image/x-icon">
  <link rel="apple-touch-icon" href="<?=$websiteUrl?>/favicon.ico?v=<?=$version?>?v=<?=$version?>" />
  <link rel="stylesheet" href="<?=$websiteUrl?>/files/css/style.css?v=<?=$version?>" />
</head>
<script type="text/javascript">
var movie = {
    id: "<?=$animeID?>"
}
var episode_play = {
    "id": "<?=$EPISODE_NUMBER?>"
}
var site_config = {
    'domain': 'anikatsu.me',
    'disqus': 'random-co6vnxqche.disqus.com',
}
</script>

<body data-page="movie_watch">
    <div id="sidebar_menu_bg"></div>
    <div id="wrapper" data-page="movie_watch">
        <?php include('./_php/header.php');?>
        <div class="clearfix"></div>
        <div id="main-wrapper" date-page="movie_watch" data-id="">
            <div id="ani_detail">
                <div class="ani_detail-stage">
                    <div class="container">
                        <div class="anis-cover-wrap">
                            <div class="anis-cover" style="background-image: url('<?=$getAnime['imageUrl']?>')">
                            </div>
                        </div>
                        <div class="anis-watch-wrap">
                            <div class="prebreadcrumb">
                                <nav aria-label="breadcrumb">
                                    <ol class="breadcrumb">
                                        <li itemprop="itemListElement" itemscope=""
                                            itemtype="http://schema.org/ListItem" class="breadcrumb-item">
                                            <a itemprop="item" href="/"><span itemprop="name">Home</span></a>
                                            <meta itemprop="position" content="1">
                                        </li>
                                        <li itemprop="itemListElement" itemscope=""
                                            itemtype="http://schema.org/ListItem" class="breadcrumb-item">
                                            <a itemprop="item" href="/anime"><span itemprop="name">Anime</span></a>
                                            <meta itemprop="position" content="2">
                                        </li>
                                        <li itemprop="itemListElement" itemscope=""
                                            itemtype="http://schema.org/ListItem" class="breadcrumb-item"
                                            aria-current="page">
                                            <a itemprop="item" href="/anime/<?=$animeID?>"><span
                                                    itemprop="name"><?=$getAnime['name']?></span></a>
                                            <meta itemprop="position" content="3">
                                        </li>
                                        <li itemprop="itemListElement" itemscope=""
                                            itemtype="http://schema.org/ListItem" class="breadcrumb-item"
                                            aria-current="page">
                                            <span itemprop="name">Episode <?=$getEpisode['ep_num']?></span>
                                            <meta itemprop="position" content="4">
                                        </li>
                                    </ol>
                                </nav>
                            </div>
                            <div class="anis-watch anis-watch-tv">
                                <div class="watch-player">
                                    <div class="player-frame">
                                        <div class="loading-relative loading-box" id="embed-loading">
                                            <div class="loading">
                                                <div class="span1"></div>
                                                <div class="span2"></div>
                                                <div class="span3"></div>
                                            </div>
                                        </div>


                                        <iframe src="https://player.animezia.net/?id=<?=$url?>" name="iframe-to-load" frameborder="0"
                                            scrolling="no"
                                            allow="accelerometer;autoplay;encrypted-media;gyroscope;picture-in-picture"
                                            allowfullscreen="true" webkitallowfullscreen="true"
                                            mozallowfullscreen="true"></iframe>
                                    </div>
                                    <div class="player-controls">
                                        <div class="pc-item pc-resize">
                                            <a href="javascript:;" id="media-resize" class="btn btn-sm"><i
                                                    class="fas fa-expand mr-1"></i>Expand</a>
                                        </div>
                                        <div class="pc-item pc-toggle pc-light">
                                            <div id="turn-off-light" class="toggle-basic">
                                                <span class="tb-name"><i class="fas fa-lightbulb mr-2"></i>Light</span>
                                                
                                            </div>
                                        </div>
                                        <div class="pc-item pc-download">
                                            <a class="btn btn-sm pc-download" href="https://animezia.net/download.php?id=<?php echo $url;  ?>" target="_blank"><i
                                                    class="fas fa-download mr-2"></i>Download</a>
                                        </div>
                                        
                                        <div class="pc-right">
                                            <?php if($getEpisode['prevEpText'] == "") {
                                            echo "";
                                        } else { ?>
                                            <div class="pc-item pc-control block-prev">
                                                <a class="btn btn-sm btn-prev"
                                                    href="/watch<?=$getEpisode['prevEpLink']?>"><i
                                                        class="fas fa-backward mr-2"></i>Prev</a>
                                            </div>&nbsp;
                                            <?php } ?>
                                            <?php if($getEpisode['nextEpText'] == "") {
                                            echo "";
                                        } else { ?>
                                            <div class="pc-item pc-control block-next">
                                                <a class="btn btn-sm btn-next"
                                                    href="/watch<?=$getEpisode['nextEpLink']?>"><i
                                                        class="fas fa-forward ml-2"></i>Next</a>
                                            </div>
                                            <?php } ?>
                                            <div class="pc-item pc-fav" id="watch-list-content"></div>
                                            <div class="pc-item pc-download" style="display:none;">
                                                <a class="btn btn-sm pc-download"><i
                                                        class="fas fa-download mr-2"></i>Download</a>
                                            </div>
                                        </div>
                                        <div class="clearfix"></div>
                                    </div>
                                </div>
                                <div class="player-servers">
                                    <div id="servers-content">
                                        <div class="ps_-status">
                                            <div class="content">
                                                <div class="server-notice"><strong>Currently watching <b>Episode
                                                            <?=$getEpisode['ep_num']?>
                                                            <br>
                                                            <span id="episodeTitle"></span></b></strong> Switch to
                                                    alternate
                                                    servers in case of error.</div>
                                            </div>
                                        </div>
                                        <div class="ps_-block ps_-block-sub servers-mixed">
                                            <div class="ps__-title"><i class="fas fa-server mr-2"></i>SERVERS:</div>
                                            <div class="ps__-list">
                                                <div class="item">
                                                    <a id="server1"
                                                        href="https://player.animezia.net/?id=<?=$url?>"
                                                        target="iframe-to-load" class="btn btn-server active">AnimeZia</a>
                                                </div>
                                                <div class="item">
                                                    <a id="server2"
                                                        href="https://player.animezia.net/?id=<?=$url?>"
                                                        target="iframe-to-load" class="btn btn-server">AnimeZia V2</a>
                                                </div>
                                                <div class="item">
                                                    <a id="server3"
                                                        href="<?=$getEpisode['video']?>"
                                                        target="iframe-to-load" class="btn btn-server">GogoServer</a>
                                                </div>
                                            </div>
                                            <div class="clearfix"></div>
                                            <div id="source-guide"></div>
                                        </div>
                                    </div>
                                </div>

                                <div id="episodes-content">
                                    <div class="seasons-block seasons-block-max">
                                        <div id="detail-ss-list" class="detail-seasons">
                                            <div class="detail-infor-content">
                                                <div style="min-height:43px;" class="ss-choice">
                                                    <div class="ssc-list">
                                                        <div id="ssc-list" class="ssc-button">
                                                            <div class="ssc-label">List of episodes:</div>
                                                        </div>
                                                    </div>
                                                    <div class="ssc-quick">
                                                        <div class="sscq-icon"><i class="fas fa-search"></i></div>
                                                        <input id="search-ep" class="form-control" type="text"
                                                            placeholder="Search EP #" autocomplete="off">
                                                    </div>
                                                    <div class="clearfix"></div>
                                                </div>
                                                <div id="episodes-page-1" class="ss-list ss-list-min" data-page="1"
                                                    style="display:block;">

                                                    <?php 
                                                    foreach ($episodelist as $episodelist) {  ?>
                                                    <a data-number="<?=$episodelist['episodeNum']?>"
                                                        id="<?=$episodelist['episodeNum']?>"
                                                        data-id="<?=$episodelist['episodeNum']?>"
                                                        title="Episode <?=$episodelist['episodeNum']?>"
                                                        class="ssl-item ep-item <?php if ($getEpisode['ep_num'] === $episodelist['episodeNum']) {echo 'active';}?>"
                                                        href="/watch/<?=$episodelist['episodeId']?>">
                                                        <div class="ssli-order" title=""><?=$episodelist['episodeNum']?>
                                                        </div>
                                                        <div class="ssli-detail">
                                                            <div class="ep-name dynamic-name" data-jname="" title="">
                                                            </div>
                                                        </div>
                                                        <div class="ssli-btn">
                                                            <div class="btn btn-circle"><i class="fas fa-play"></i>
                                                            </div>
                                                        </div>
                                                        <div class="clearfix"></div>
                                                    </a>
                                                    <?php } ?>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="clearfix"></div>
                                    </div>
                                </div>
                            </div>
                            <div class="anis-watch-detail">
                                <div class="anis-content">
                                    <div class="anisc-poster">
                                        <div class="film-poster">
                                            <img src="<?=$getAnime['imageUrl']?>" data-src="<?=$getAnime['imageUrl']?>"
                                                class="film-poster-img ls-is-cached lazyloaded"
                                                alt="<?=$getAnime['name']?>">
                                        </div>
                                    </div>
                                    <div class="anisc-detail">
                                        <h2 class="film-name">
                                            <a href="/anime/<?=$anime?>" class="text-white dynamic-name"
                                                title="<?=$getAnime['name']?>" data-jname="<?=$getAnime['name']?>"
                                                style="opacity: 1;"><?=$getAnime['name']?></a>
                                        </h2>
                                        <div class="film-stats">
                                            <div class="tac tick-item tick-quality">HD</div>
                                            <div class="tac tick-item tick-dub"><?php $str = $getAnime['name'];
                                          $last_word_start = strrpos ( $str , " ") + 1;
                                          $last_word_end = strlen($str) - 1;
                                          $last_word = substr($str, $last_word_start, $last_word_end);
                                          if ($last_word == "(Dub)"){echo "DUB";} else {echo "SUB";}
                                          ?></div>
                                            <div class="tac tick-item tick-views">
                                                <?php if($counter){echo "VIEWS: ".$counter;};?></div>
                                            <span class="dot"></span>
                                            <span class="item"><?=$getAnime['status']?></span>
                                            <span class="dot"></span>
                                            <span class="item"><?=$getAnime['released']?></span>
                                            <span class="dot"></span>
                                            <span class="item"><?=$getAnime['othername']?></span>
                                            <span class="dot"></span>
                                            <span class="item"><?=$getAnime['type']?></span>
                                            <div class="clearfix"></div>
                                        </div>
                                        <div class="film-description m-hide">
                                            <div class="text"><?=$getAnime['synopsis']?></div>
                                        </div>
                                        <div class="film-text m-hide mb-3">
                                           
                                        </div>
                                        <div class="block"><a href="/anime/<?=$anime?>" class="btn btn-xs btn-light"><i
                                                    class="fas fa-book-open mr-2"></i> View detail</a></div>


                                        <?php
                                        $likeClass="far";	
			                            if(isset($_COOKIE['like_'.$id])){
			                            	$likeClass="fas";
			                            }		
                            
			                            $dislikeClass="far";	
			                            if(isset($_COOKIE['dislike_'.$id])){
			                            	$dislikeClass="fas";
			                            }	
                                        ?>
                                        <div class="dt-rate">
                                            <div id="vote-info">
                                                <div class="block-rating">
                                                    <div class="rating-result">
                                                        <div class="rr-mark float-left">
                                                            <strong><i class="fas fa-star text-warning mr-2"></i><span
                                                                    id="ratingAnime"><?=round((10*$like_count + 5*$dislike_count)/($like_count+$dislike_count),2)?></span></strong>
                                                            <small id="votedCount">(<?php 
                                                                if(isset($totalVotes)){
                                                                echo $totalVotes;
                                                                }?> Voted)</small>
                                                        </div>
                                                        <div class="rr-title float-right">Vote now</div>
                                                        <div class="clearfix"></div>
                                                    </div>
                                                    <div class="description">What do you think about this anime?</div>
                                                    <div class="button-rate">
                                                        <button type="button"
                                                            onclick="setLikeDislike('dislike','<?=$id?>')"
                                                            class="btn btn-emo rate-bad btn-vote" style="width:50%"
                                                            data-mark="dislike"><i id="dislike"
                                                                class="<?php echo $dislikeClass?> fa-thumbs-down">
                                                            </i><span id="dislikeMsg"
                                                                class="ml-2">Dislike</span></button>
                                                        <button onclick="setLikeDislike('like','<?=$id?>')"
                                                            type="button" class="btn btn-emo rate-good btn-vote"
                                                            style="width:50%"><i id="like"
                                                                class="<?php echo $likeClass?> fa-thumbs-up"> </i><span
                                                                id="likeMsg" class="ml-2">Like</span></button>
                                                        <div class="clearfix"></div>
                                                    </div>
                                                    <div class="clearfix"></div>
                                                </div>
                                            </div>
                                        </div>
                                        </a>

                                    </div>

                                    <div class="clearfix"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <?php include('./_php/ads/728x90.html')?>
            <div class="container">
                <div id="main-content">
                    <section class="block_area block_area-comment">
                        <div class="block_area-header block_area-header-tabs">
                            <div class="float-left bah-heading mr-4">
                                <h2 class="cat-heading">Comments</h2>
                            </div>
                            <div class="clearfix"></div>
                        </div>
                        <div class="tab-content">
                          <?php include('./_php/disqus.php'); ?>
                        </div>
                    </section>
                </div>
                <?php include('./_php/sidenav.php'); ?>
                <div class="clearfix"></div>
            </div>
        </div>
        <?php include('./_php/footer.php'); ?>
        <div id="mask-overlay"></div>
        <script type="text/javascript"
            src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js?v=<?=$version?>"></script>
        <script type="text/javascript"
            src="https://maxcdn.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.bundle.min.js?v=<?=$version?>"></script>
        <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/js-cookie@rc/dist/js.cookie.min.js"></script>
        <script type="text/javascript" src="<?=$websiteUrl?>/files/js/app.js?v=<?=$version?>"></script>
        <script type="text/javascript" src="<?=$websiteUrl?>/files/js/comman.js?v=<?=$version?>"></script>
        <script type="text/javascript" src="<?=$websiteUrl?>/files/js/movie.js?v=<?=$version?>"></script>
        <link rel="stylesheet" href="<?=$websiteUrl?>/files/css/jquery-ui.css?v=<?=$version?>">
        <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js?v=<?=$version?>"></script>
        <script type="text/javascript">
        $(".btn-server").click(function() {
            $(".btn-server").removeClass("active");
            $(this).closest(".btn-server").addClass("active");
        });
        </script>
        <script type="text/javascript">
        if ('<?=$likeClass?>' === 'fas') {
            document.getElementById('likeMsg').innerHTML = "Liked"
        }
        if ('<?=$dislikeClass?>' === 'fas') {
            document.getElementById('dislikeMsg').innerHTML = "Disliked"
        }

        function setLikeDislike(type, id) {
            jQuery.ajax({
                url: '<?=$websiteUrl?>/setLikeDislike.php',
                type: 'post',
                data: 'type=' + type + '&id=' + id,
                success: function(result) {
                    result = jQuery.parseJSON(result);
                    if (result.opertion == 'like') {
                        jQuery('#like').removeClass('far');
                        jQuery('#like').addClass('fas');
                        jQuery('#dislike').addClass('far');
                        jQuery('#dislike').removeClass('fas');
                        jQuery('#likeMsg').html("Liked")
                        jQuery('#dislikeMsg').html("Dislike")
                    }
                    if (result.opertion == 'unlike') {
                        jQuery('#like').addClass('far');
                        jQuery('#like').removeClass('fas');
                        jQuery('#likeMsg').html("Like")
                    }

                    if (result.opertion == 'dislike') {
                        jQuery('#dislike').removeClass('far');
                        jQuery('#dislike').addClass('fas');
                        jQuery('#like').addClass('far');
                        jQuery('#like').removeClass('fas');
                        jQuery('#dislikeMsg').html("Disliked")
                        jQuery('#likeMsg').html("Like")
                    }
                    if (result.opertion == 'undislike') {
                        jQuery('#dislike').addClass('far');
                        jQuery('#dislike').removeClass('fas');
                        jQuery('#dislikeMsg').html("Dislike")
                    }


                    jQuery('#votedCount').html(
                        `(${parseInt(result.like_count) + parseInt(result.dislike_count)} Voted)`
                    );
                    jQuery('#ratingAnime').html(((parseInt(result.like_count) *
                        10 + parseInt(result.dislike_count) * 5) / (
                        parseInt(result.like_count) + parseInt(
                            result.dislike_count))).toFixed(2));
                }

            });
        }
        </script>
    </div>
</body>

</html>