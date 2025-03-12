<?php require('_config.php'); 
session_start();

?>
<!DOCTYPE html>
<html lang="en">

<head>
    <title>Contact Form - <?=$websiteTitle?></title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="robots" content="index,follow" />
    <meta http-equiv="content-language" content="en" />
    <meta name="description" content="Have a query? Contact <?=$websiteTitle?>" />
    <meta name="keywords" content="anime to watch, watch anime,anime online, free anime online, online anime, anime streaming, stream anime online, english anime, english dubbed anime" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="<?=$websiteUrl?>/contact" />
    <meta property="og:title" content="Contact Form - <?=$websiteTitle?>" />
    <meta property="og:image" content="<?=$banner?>" />
    <meta property="og:description" content="Have a query? Contact <?=$websiteTitle?>" />
    <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1" />
    <link rel="shortcut icon" href="<?=$websiteUrl?>/favicon.ico?v=<?=$version?>" type="image/x-icon">
    <link rel="apple-touch-icon" href="<?=$websiteUrl?>/favicon.ico?v=<?=$version?>" />
    <link rel="stylesheet" href="<?=$websiteUrl?>/files/css/style.css?v=<?=$version?>">
    
    <link rel="stylesheet" href="<?=$websiteUrl?>/files/css/min.css?v=<?=$version?>">
    <script type="text/javascript">
        setTimeout(function () {
            var wpse326013 = document.createElement('link');
            wpse326013.rel = 'stylesheet';
            wpse326013.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta2/css/all.min.css?v=<?=$version?>';
            wpse326013.type = 'text/css';
            var godefer = document.getElementsByTagName('link')[0];
            godefer.parentNode.insertBefore(wpse326013, godefer);
            var wpse326013_2 = document.createElement('link');
            wpse326013_2.rel = 'stylesheet';
            wpse326013_2.href = 'https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.4.1/css/bootstrap.min.css?v=<?=$version?>';
            wpse326013_2.type = 'text/css';
            var godefer2 = document.getElementsByTagName('link')[0];
            godefer2.parentNode.insertBefore(wpse326013_2, godefer2);
        }, 500);
    </script>
    <noscript>
        <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta2/css/all.min.css?v=<?=$version?>" />
        <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.4.1/css/bootstrap.min.css?v=<?=$version?>" />
    </noscript>
 
</head>

<body>
    <div id="sidebar_menu_bg"></div>
    <div id="wrapper">
        <?php include("./_php/header.php"); ?>
        <div class="clearfix"></div>
        <div id="main-wrapper" class="layout-page layout-page-infor">
            <div class="information_page">
                <div class="container">
                    <div class="information_page-wrap">
                        <div class="prebreadcrumb">
                            <nav aria-label="breadcrumb">
                                <ol class="breadcrumb">
                                    <li class="breadcrumb-item"><a href="/">Home</a></li>
                                    <li class="breadcrumb-item active" aria-current="page">Contact</li>
                                </ol>
                            </nav>
                        </div>
                        <div class="information_page-content">
                            <h2 class="h2-heading">Contact Us</h2>
                            <p>Please submit your inquiry using the form below and we will get in touch with you
                                shortly.</p>
                            <div class="contact-social-icons mt-4 mb-4">
                                <div class="block">
                                    <a href="<?=$twitter?>" target="_blank" class="btn btn-radius">
                                        <div class="icon-rounder icon-rounder-twitter"><i class="fab fa-twitter"></i>
                                        </div>
                                        <div class="csib-link">Twitter</div>
                                        <div class="clearfix"></div>
                                    </a>
                                </div>
                                <div class="block">
                                    <a href="<?=$telegram?>" target="_blank"
                                        class="btn btn-radius">
                                        <div class="icon-rounder icon-rounder-telegram"><i
                                                class="fab fa-telegram-plane"></i></div>
                                        <div class="csib-link">Telegram</div>
                                        <div class="clearfix"></div>
                                    </a>
                                </div>
                                <div class="block">
                                    <a href="<?=$discord?>" target="_blank" class="btn btn-radius">
                                        <div class="icon-rounder icon-rounder-discord"><i class="fab fa-discord"></i>
                                        </div>
                                        <div class="csib-link">Discord</div>
                                        <div class="clearfix"></div>
                                    </a>
                                </div>
                                <div class="block">
                                    <a href="<?=$reddit?>" target="_blank" class="btn btn-radius">
                                        <div class="icon-rounder icon-rounder-reddit"><i
                                                class="fab fa-reddit-alien"></i></div>
                                        <div class="csib-link">Reddit</div>
                                        <div class="clearfix"></div>
                                    </a>
                                </div>
                                <div class="clearfix"></div>
                            </div>
                            <div class="row">
                                <div class="col-xl-6 col-lg-8 col-md-12">
                                    <form id="contact-form" method="post">
                                        <div class="form-group">
                                            <label for="contact-email">Your email</label>
                                            <input type="email" class="form-control" id="contact-email" name="email"
                                                required placeholder="name@example.com">
                                        </div>
                                        <div class="form-group">
                                            <label for="contact-subject">Subject</label>
                                            <input type="text" class="form-control" name="subject" id="contact-subject"
                                                required>
                                        </div>
                                        <div class="form-group">
                                            <label for="contact-message">Message</label>
                                            <textarea class="form-control form-control-textarea" id="contact-message"
                                                required rows="10" cols="3" name="message" maxlength="3000"></textarea>
                                        </div>
                                        <div class="form-group">
                                            <div class="mt-5"></div>
                                            <button class="btn btn-block btn-lg btn-focus">Submit</button>
                                            <div class="loading-relative" id="contact-loading" style="display: none;">
                                                <div class="loading">
                                                    <div class="span1"></div>
                                                    <div class="span2"></div>
                                                    <div class="span3"></div>
                                                </div>
                                            </div>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <?php include('./_php/footer.php'); ?>
    </div>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js?v=<?=$version?>"></script>
    <script type="text/javascript" src="https://maxcdn.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.bundle.min.js?v=<?=$version?>"></script>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/js-cookie@rc/dist/js.cookie.min.js"></script>
    <script type="text/javascript" src="<?=$websiteUrl?>/files/js/app.js?v=<?=$version?>"></script>
    <link rel="stylesheet" href="<?=$websiteUrl?>/files/css/jquery-ui.css?v=<?=$version?>">
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js?v=<?=$version?>"></script>
</body>

</html>