<?php


function navigationButtons($summary){
    global $user, $management, $labels, $settings,$buttons,$details,$buttons1,$details1,$buttons2,$details2,$buttons3,$details3;
    $user =['button green', 'User'];
    $management =['button', 'Management'];
    $labels =['button orange', 'Labels'];
    $settings =['button gray', 'Settings'];

    if ($summary == 'User') {
        $buttons = $user[0];
        $details = $user[1];
        $buttons1 = $management[0];
        $details1 = $management[1];
        $buttons2 = $labels[0];
        $details2 = $labels[1];
        $buttons3 = $settings[0];
        $details3 = $settings[1];
    }

    if ($summary == 'Management') {
        $buttons = $management[0];
        $details = $management[1];
        $buttons1 = $user[0];
        $details1 = $user[1];
        $buttons2 = $labels[0];
        $details2 = $labels[1];
        $buttons3 = $settings[0];
        $details3 = $settings[1];
    }




}

?> 
