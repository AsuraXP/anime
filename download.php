<?php
// Get the 'id' from the URL
$id = isset($_GET['id']) ? $_GET['id'] : null;
$downloadData = null;

// Initialize variables for next and previous episodes
$animeName = "";
$currentEpisode = 0;
$nextEpisodeId = null;
$prevEpisodeId = null;
$previewUrl = null;

if ($id) {
    // Parse the anime name and episode number from the ID
    if (preg_match('/(.*)-episode-(\d+)/i', $id, $matches)) {
        $animeName = $matches[1];
        $currentEpisode = (int)$matches[2];

        // Generate IDs for next and previous episodes
        $nextEpisodeId = "{$animeName}-episode-" . ($currentEpisode + 1);
        if ($currentEpisode > 1) {
            $prevEpisodeId = "{$animeName}-episode-" . ($currentEpisode - 1);
        }

        // Generate the preview URL for iframe
        $previewUrl = "https://player.animezia.net/?id={$id}";
    }

    // Construct the API URL
    $apiUrl = "https://api-47i0.onrender.com/api/v1/download/{$id}";
    $response = file_get_contents($apiUrl);
    if ($response) {
        $downloadData = json_decode($response, true);
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Download Page</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        /* General Styles */
        body {
            background-color: #011f2b; /* Dark Blue background */
            color: #e0f1f7; /* Light blue text */
            font-family: 'Poppins', sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }

        .container {
            width: 100%;
            max-width: 900px;
            padding: 20px;
        }

        /* Card Styles */
        .card {
            background-color: #0a2a3d; /* Lighter blue background */
            border: 1px solid #123f57;
            border-radius: 15px;
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.8);
            padding: 30px;
            text-align: center;
            animation: fadeIn 1s ease-out;
        }

        h1 {
            font-size: 2.8rem;
            color: #1d83c1; /* Blue for header */
            margin-bottom: 25px;
        }

        p {
            font-size: 1rem;
            color: #a1c4d3; /* Soft text color */
        }

        /* Button Styles */
        .download-buttons {
            margin-top: 30px;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
        }

        .download-button {
            background: linear-gradient(135deg, #1d83c1, #3498db); /* Gradient blue */
            color: #fff;
            border: none;
            padding: 15px 20px;
            font-size: 1rem;
            text-transform: uppercase;
            border-radius: 5px;
            min-width: 200px;
            transition: transform 0.3s, background-color 0.3s;
        }

        .download-button:hover {
            transform: scale(1.05);
            background: linear-gradient(135deg, #3498db, #4a90e2);
        }

        /* Navigation Buttons */
        .nav-buttons {
            margin-top: 50px;
            display: flex;
            justify-content: space-between;
            gap: 20px;
        }

        .nav-button {
            background: #123f57;
            color: #1d83c1;
            border: 2px solid #1d83c1;
            padding: 10px 25px;
            font-size: 1rem;
            text-transform: uppercase;
            border-radius: 8px;
            text-decoration: none;
            transition: all 0.3s ease;
        }

        .nav-button:hover {
            background-color: #1d83c1;
            color: #fff;
        }

        .nav-button:disabled {
            border-color: #555;
            color: #555;
            background-color: #0a2a3d;
            cursor: not-allowed;
        }

        /* Iframe Styles */
        .preview-iframe {
            width: 100%;
            height: 450px;
            border: none;
            border-radius: 10px;
            margin-top: 30px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.7);
        }

        /* Fade-in Animation */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Media Queries for Mobile */
        @media (max-width: 768px) {
            h1 {
                font-size: 2rem;
            }

            /* Download buttons should be centered above the anime name */
            .download-buttons {
                flex-direction: column;
                align-items: center;
                margin-top: 15px;
            }

            .download-button {
                width: 80%;
                min-width: 150px;
                margin-bottom: 10px;
            }

            .card {
                padding: 15px;
            }

            .nav-buttons {
                flex-direction: column;
                align-items: center;
            }

            .nav-button {
                width: 80%;
                margin-bottom: 10px;
            }

            .preview-iframe {
                height: 250px;
                margin-top: 20px;
            }
        }

        /* For very small screens (portrait smartphones) */
        @media (max-width: 480px) {
            .preview-iframe {
                height: 200px;
            }

            .download-button {
                font-size: 0.9rem;
                padding: 12px 15px;
            }

            .nav-button {
                padding: 8px 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <!-- Reposition Download Buttons Above the Anime Name for Mobile -->
            <?php if ($downloadData): ?>
                <div class="download-buttons">
                    <?php foreach ($downloadData['raw'] as $link): ?>
                        <a href="<?= $link['url'] ?>" class="download-button" target="_blank">
                            Download (<?= htmlspecialchars($link['resolution']) ?>)
                        </a>
                    <?php endforeach; ?>
                </div>
            <?php else: ?>
                <p>No download data available.</p>
            <?php endif; ?>

            <h1><?= $id ? htmlspecialchars($id) : 'Download Page' ?></h1>

            <!-- Iframe Preview -->
            <?php if ($previewUrl): ?>
                <iframe src="<?= $previewUrl ?>" class="preview-iframe"></iframe>
            <?php endif; ?>

            <!-- Navigation Buttons -->
            <div class="nav-buttons">
                <?php if ($prevEpisodeId): ?>
                    <a href="?id=<?= $prevEpisodeId ?>" class="nav-button">Previous Episode</a>
                <?php else: ?>
                    <button class="nav-button" disabled>Previous Episode</button>
                <?php endif; ?>

                <?php if ($nextEpisodeId): ?>
                    <a href="?id=<?= $nextEpisodeId ?>" class="nav-button">Next Episode</a>
                <?php endif; ?>
            </div>
        </div>
    </div>
</body>
</html>
