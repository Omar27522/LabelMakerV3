<?php

$uri = ucfirst(ltrim($_SERVER['REQUEST_URI'], " /?"));

if(isset($_GET['returnsDepartment'])) {
    
    $title = $uri;
}
else if(isset($_GET['dailyTasks'])) {
    $title = $uri;
}
else if(isset($_GET['software'])) {
    $title = $uri;
}
else if(isset($_GET['inspections'])) {
    $title = $uri;
   
}
else if(isset($_GET['labeling'])) {
    $title = $uri;
}
else if(isset($_GET['palletizing'])) {
    $title = $uri;
}
else    { 
$title="JDL Returns Department";
}

 include 'menu/header.php';


if(isset($_GET['returnsDepartment'])) {
    
    include './returnsDepartment.php';
}
else if(isset($_GET['dailyTasks'])) {
    include './dailyTasks.php';
}
else if(isset($_GET['software'])) {
    include './software.php';
}
else if(isset($_GET['inspections'])) {
    include './inspection.php';
   
}
else if(isset($_GET['labeling'])) {
    include './labeling.php';
}
else if(isset($_GET['palletizing'])) {
    include './palletizing.php';
}
else    { ?>
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