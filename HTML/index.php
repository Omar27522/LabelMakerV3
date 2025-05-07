<?php

$uri = ucfirst(ltrim($_SERVER['REQUEST_URI'], " /?"));

if(isset($_GET['returnsDepartment'])) {
    $title = $uri;
    include 'menu/header.php';
    include './returnsDepartment.php';
}
else if(isset($_GET['dailyTasks'])) {
    $title = $uri;
    include 'menu/header.php';
    include './dailyTasks.php';
}
else if(isset($_GET['inspections'])) {
    $title = $uri;
    include 'menu/header.php';
    include './inspection.php';
}
else if(isset($_GET['labeling'])) {
    $title = $uri;
    include 'menu/header.php';
    include './labeling.php';
}
else if(isset($_GET['palletizing'])) {
    $title = $uri;
    include 'menu/header.php';
    include './palletizing.php';
}
else    { 
    $title="JDL Returns Department";
    include 'menu/header.php';
?>
<section>
<h1>JDL
    Returns
    DEPARTMENT</h1>
<h2>5.1.2025</h2>
<?php
 //echo $_SERVER['REQUEST_URI'];
?>

<a href="?returnsDepartment"><button><h2>CONFERENCE / EVENT PRESENTATION</h2></button></a>
<h2>PRESENTATOR: Miguel Garcia</h2>
<h2>BY OSI Staffing</h2>
    </section>
<?php
}
include 'menu/footer.php'; 
?>