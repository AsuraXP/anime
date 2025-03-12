<?php 
require_once('./_config.php');
$parts=parse_url($_SERVER['REQUEST_URI']); 
$page_url=explode('/', $parts['path']);
$url = $page_url[count($page_url)-1];
//$url = "naruto";

$getAnime = file_get_contents("$api/getAnime/$url");
$getAnime = json_decode($getAnime, true);
$episodelist = $getAnime['episode_id'];
?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" itemscope="" itemtype="http://schema.org/WebPage" lang="en-US">
<head prefix="og: http://ogp.me/ns# fb: http://ogp.me/ns/fb# article: http://ogp.me/ns/article#">
     <meta charset="UTF-8" />
     <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
     <link rel="profile" href="https://gmpg.org/xfn/11">
   
     <link rel="shortcut icon" href="/favicon.ico">
   
     <title>Watch <?=$getAnime['name']?>  free on <?=$websiteTitle?> | Chromecast Available</title>
     <meta name="keywords" content="crunchyroll,9anime,gogoanime,aniwatch,animesuge">
   
     <meta name="robots" content="index, follow" />
     
     <meta name="description" content="Watch <?=$getAnime['name']?> online free in HD on <?=$websiteTitle?> | Chromecast Available" />
   
   
     <meta itemprop="image" content="/logo.png" />
   
     <meta property="og:site_name" content="Ryuk" />
     <meta property="og:locale" content="en_US" />
     <meta property="og:type" content="website" />
     <meta property="og:image" content="/logo.png">
    <link rel="stylesheet" href="<?=$websiteUrl?>/files/css/style.css?v=<?=$version?>">
    <link rel="stylesheet" href="<?=$websiteUrl?>/files/css/min.css?v=<?=$version?>">
    <script type="text/javascript">
        setTimeout(function () {
            var wpse326013 = document.createElement('link');
            wpse326013.rel = 'stylesheet';
            wpse326013.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta2/css/all.min.css';
            wpse326013.type = 'text/css';
            var godefer = document.getElementsByTagName('link')[0];
            godefer.parentNode.insertBefore(wpse326013, godefer);
            var wpse326013_2 = document.createElement('link');
            wpse326013_2.rel = 'stylesheet';
            wpse326013_2.href = 'https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.4.1/css/bootstrap.min.css';
            wpse326013_2.type = 'text/css';
            var godefer2 = document.getElementsByTagName('link')[0];
            godefer2.parentNode.insertBefore(wpse326013_2, godefer2);
        }, 500);
    </script>
    <noscript>
        <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta2/css/all.min.css" />
        <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.4.1/css/bootstrap.min.css" />
    </noscript>
</head>

<body data-page="movie_info">
    <div id="sidebar_menu_bg"></div>
    <div id="wrapper" data-page="page_home">
        <?php include('./_php/header.php'); ?>
        <div class="clearfix"></div>
        <div id="main-wrapper" date-page="movie_info" data-id="<?=$url?>">
            <div id="ani_detail">
                <div class="ani_detail-stage">
                    <div class="container">
                        <div class="anis-cover-wrap">
                            <div class="anis-cover"
                                style="background-image: url('<?=$getAnime['imageUrl']?>')"></div>
                        </div>
                        <div class="anis-content">
                            <div class="anisc-poster">
                                <div class="film-poster">
                                    <img src="<?=$websiteUrl?>/files/images/no_poster.jpg"
                                        data-src="<?=$getAnime['imageUrl']?>"
                                        class="lazyload film-poster-img">
                                </div>
                            </div>
                            <div class="anisc-detail">
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
                                                itemtype="http://schema.org/ListItem"
                                                class="breadcrumb-item dynamic-name" data-jname="<?=$getAnime['name']?>"
                                                aria-current="page">
                                                <a itemprop="item" href="/anime/<?=$url?>"><span itemprop="name"><?=$getAnime['name']?></span></a>
                                                <meta itemprop="position" content="3">
                                            </li>
                                        </ol>
                                    </nav>
                                </div>
                                <h2 class="film-name dynamic-name" data-jname="<?=$getAnime['name']?>"><?=$getAnime['name']?></h2>
                                <div class="film-stats">
                                    <div class="tac tick-item tick-quality">HD</div>
                                    <div class="tac tick-item tick-dub">
                                    <?php $str = $getAnime['name'];
                                          $last_word_start = strrpos ( $str , " ") + 1;
                                          $last_word_end = strlen($str) - 1;
                                          $last_word = substr($str, $last_word_start, $last_word_end);
                                          if ($last_word == "(Dub)"){echo "DUB";} else {echo "SUB";}
                                    ?>
                                    </div>
                                    <span class="dot"></span>
                                    <span class="item"><?=$getAnime['type']?></span>
                                    <div class="clearfix"></div>
                                </div>
                                <?php if(count($getAnime['episode_id']) == 0) {
                                    echo "";
                                } else { ?>
                                <div class="film-buttons">
                                    <a href="/watch/<?php foreach(array_slice($episodelist, 0, 1) as $episode1) {?><?=$episode1['episodeId']?><?php } ?>" class="btn btn-radius btn-primary btn-play"><i
                                            class="fas fa-play mr-2"></i>Watch now</a>

                                            <div class="dr-fav" id="watch-list-content">


                                        <?php } ?>

                                        <div class="dr-fav" id="watch-list-content">

                                            <?php if(isset($_COOKIE['userID'])){?>
                                            <?php 
                                             $watchLater = mysqli_query($conn, "SELECT * FROM `watch_later` WHERE (user_id,anime_id) = ('$user_id','$url')"); 
                                             $watchLater = mysqli_fetch_assoc($watchLater); 
                                             if(isset($watchLater['anime_id'])){
                                             $anime_id = $watchLater['anime_id'];
                                             }else{
                                                $anime_id = null;
                                             }
                                             if($anime_id == null){ ?>
                                            <a id="addToList" class="btn btn-radius btn-light"
                                                animeId="<?=$url?>">&nbsp;<i class='fas fa-plus mr-2'></i> Add to
                                                List&nbsp;</a>
                                            <script>
                                            let btn = document.querySelector('#addToList');
                                            btn.addEventListener("click", () => {
                                                let btnValue = btn.getAttribute('animeId');
                                                $.post('../user/ajax/watchlist.php', {
                                                    btnValue: btnValue
                                                }, (response) => {
                                                    btn.innerHTML = response;

                                                });
                                            });
                                            </script>
                                            <?php }elseif($anime_id == $url){ ?>
                                            <a id="addToList" class="btn btn-radius btn-light"
                                                animeId="<?=$url?>">&nbsp;<i class='fas fa-minus mr-2'></i> Remove From
                                                List&nbsp;</a>
                                            <script>
                                            let btn = document.querySelector('#addToList');
                                            btn.addEventListener("click", () => {
                                                let btnValue = btn.getAttribute('animeId');
                                                $.post('../user/ajax/watchlist.php', {
                                                    btnValue: btnValue
                                                }, (response) => {
                                                    btn.innerHTML = response;

                                                });
                                            });
                                            </script>
                                            <?php }?>
                                            <?php } ?>



                                            <?php if(!isset($_COOKIE['userID'])){?>
                                            <a href="<?=$websiteUrl?>/user/login?animeId=<?=$url?>"
                                                class="btn btn-radius btn-light">&nbsp;<i
                                                    class='fas fa-plus mr-2'></i>&nbsp;Login to Add&nbsp;</a>
                                            <?php } ?>
                                        </div>
                                    </div>
                                <div class="film-description m-hide">
                                    <div class="text"><?=$getAnime['synopsis']?></div>
                                </div>
                               
                            </div>
                            </div>
                            <div class="anisc-info-wrap">
                                <div class="anisc-info">
                                    <div class="item item-title w-hide">
                                        <span class="item-head">Overview:</span>
                                        <div class="text"><?=$getAnime['synopsis']?></div>
                                    </div>
                                    <div class="item item-title">
                                        <span class="item-head">Other names:</span> <span class="name"><?=$getAnime['othername']?></span>
                                    </div>
                                    <div class="item item-title">
                                        <span class="item-head">Language:</span> 
                                        <span class="name">
                                            <?php $str = $getAnime['name'];
                                                $last_word_start = strrpos ( $str , " ") + 1;
                                                $last_word_end = strlen($str) - 1;
                                                $last_word = substr($str, $last_word_start, $last_word_end);
                                                if ($last_word == "(Dub)"){echo "Dubbed";} else {echo "Subbed";}
                                            ?>
                                        </span>
                                    </div>
                                    <div class="item item-title">
                                        <span class="item-head">Episodes:</span> <span class="name"><?php echo count($getAnime['episode_id'])?></span>
                                    </div>
                                    <div class="item item-title">
                                        <span class="item-head">Release Year:</span> <span class="name"><?=$getAnime['released']?></span>
                                    </div>
                                    <div class="item item-title">
                                        <span class="item-head">Type:</span> <span class="name"><?=$getAnime['type']?></span>
                                    </div>
                                    <div class="item item-title">
                                        <span class="item-head">Status:</span> <a href="<?php if ($getAnime['status'] == "Completed") {echo "/status/completed";} else {echo "/status/ongoing";}?>"><?=$getAnime['status']?></a>
                                    </div>
                                    <div class="item item-list">
                                        <span class="item-head">Genres:</span> <?php foreach($getAnime['genres'] as $genre) { ?><a href="<?=$websiteUrl?>/genre/<?php $genreUrl = strtolower($genre); echo str_replace(" ","+", $genreUrl);?>"><?=$genre?></a><?php } ?>
                                    </div>
                                    <div class="film-text w-hide"><?=$websiteTitle?> is a site to watch online anime like <strong><?=$getAnime['name']?></strong> online, or you can even watch <strong><?=$getAnime['name']?></strong> in HD quality</div>
                                </div>
                                <div class="clearfix"></div>
                            </div>
                            <div class="clearfix"></div>
                        </div>
                    </div>
                </div>
            </div>

            <?php include("_php/ads/728x90.html"); ?>
            
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
        <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
        
        <script type="text/javascript" src="https://maxcdn.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.bundle.min.js"></script>
        <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/js-cookie@rc/dist/js.cookie.min.js"></script>
        <script type="text/javascript" src="<?=$websiteUrl?>/files/js/app.js"></script>
        <script type="text/javascript" src="<?=$websiteUrl?>/files/js/comman.js"></script>
        <script type="text/javascript" src="<?=$websiteUrl?>/files/js/movie.js"></script>
        <link rel="stylesheet" href="<?=$websiteUrl?>/files/css/jquery-ui.css">
        <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
        <script type="text/javascript" src="<?=$websiteUrl?>/files/js/function.js"></script>
    </div>
</body>

</html>