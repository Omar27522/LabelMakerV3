<?php
$uri = ucfirst(ltrim($_SERVER['REQUEST_URI'], " /?"));
$button="";
$button2 ='<button>Next</button></a>';
$button1= '<a href="?'.$button.'">';
function content($content, $button) {
    global $title,$button2,$button1,$button,$uri;
    $title = $uri;
    $button = $button1 . $button2;
    include 'menu/header.php';
    include './'.$content.'.php';
}

if(isset($_GET['returnsDepartment'])) {
    content("returnsDepartment","dailyTasks");
}
else if(isset($_GET['dailyTasks'])) {
    content("dailyTasks","software");
}
else if(isset($_GET['software'])) {
    content("software","inspections");
}
else if(isset($_GET['inspections'])) {
    content("inspections","labeling");
}
else if(isset($_GET['labeling'])) {
    content("labeling","palletizing");
}
else if(isset($_GET['palletizing'])) {
    content("palletizing","index");
}
else    { 
    $title="JDL Returns Department";
    $button1= '<a href="../">';
    $button = $button1 . $button2;
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