<?php
	class Page {

		public $title;
		public $lang;

		public function title($title){
			$this->title=$title;
		}
		public function lang($lang){
			$this->lang=$lang;
		}
		
		public function getTitle(){
			return $this->title;
		}
		public function getLanguage(){
			return $this->lang;
		}
	}

		$a = new Page();
		$a->title('Welcome');
		$a->lang('en');
?>

<!DOCTYPE html>
<html lang="<?= $a->getLanguage();?>">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <?php if (isset($_GET['software'])){
        echo '<link rel="stylesheet" href="software/styles/styles.css"><link rel="stylesheet" href="software/styles/gettingStarted.css">';
    }?>
    <title><?= $a->getTitle();?></title>
</head>

<body>
    <header>
        <nav>
            <ul>
                <details>
                    <summary>➡️</summary>
                    <li><a href="?returnsDepartment">Returns Department</a></li>
                    <li><a href="?dailyTasks">Daily Tasks</a></li>
                    <li><a href="?software">Software</a></li>
                    <li><a href="?inspections">Inspection, Grading and Sorting</a></li>
                    <li><a href="?labeling">Labeling</a></li>
                    <li><a href="?palletizing">Palletizing</a></li>
                </details>
            </ul>
        </nav>
    </header>
    <?php
		if (isset($_GET['dailyTasks'])){ ?>
    <section>
        <section>
            <h1 style="page-break-before:always; float:left">Job - Daily Tasks</h1>
            <h2 style="float:right">Here in the JDL Returns Department, we handle a variety of essential tasks to ensure
                the efficient processing of
                returned items.<br />
                <span style="font-size: 1.5rem;">AWAY Returns Department at JDL</span>
            </h2>


            <h2>Each Day:</h2>
            <h2>Team must unload a “returns” truck and account for all returned items. Once the returns are verified,
                the team
                sorts, cleans, re-boxes, re-labels, and grades the items before putting them away. Our goal is to
                maintain a
                seamless returns process and uphold the highest standards of quality and organization.</h2>
            <h2>Start:</h2>

            <aside>
                <img src="https://raw.githubusercontent.com/Omar27522/LabelMakerV3/refs/heads/main/HTML/Away%20Products/media/returns.png"
                    alt="returns" style="float:left; margin-right:1rem; width:30%;">

                <h2>We begin by processing any backlog items in the system (items sitting in the warehouse longer than
                    48hrs).</h2>
                <h2>UPS/FEDEX truck</h2>
                <h2>two or more people will help unload it. Two different products arrive, AWAY and non-away. We make
                    sure to separate
                    them during the unloading process to avoid mix ups Once everything is unloaded, all tracking numbers
                    will be
                    recorded, obtaining the total number of products that arrived, separating them into three main
                    categories: RS,
                    Non-RS, and Retail</h2>
                <p style="font-size: 2rem;font-weight: bold;">Metal Basket</p>
                <h2>Once all tracking numbers are recorded, they will be placed in a metal basket to then be transported
                    to the
                    returns department. Once they arrive, they will be removed from the baskets and placed on a pallet
                    to be wrapped and
                    counted.</h2>
            </aside>

            <section class="border">
                <h2>Returns Dept</h2>
                <aside>
                    <h2>RS</h2>
                    <h2>Non-RS</h2>
                    <h2>RETAIL</h2 </aside>
            </section>

            <h1 style="page-break-before:always; ">A label will be placed on both sides where the pallet jack enters,
                and this
                label will include the date the items arrived at the warehouse, the number of products on the pallet,and
                a legend
                stating that they are indeed RETURNS. Then the sorting, cleaning, re-boxing, re-labeling, and grading of
                the
                products begin.</h1>
            <a href="?software">
                <button>
                    Click Next
                </button>
            </a>
        </section>
        <?php }
		else if (isset($_GET['software'])) {
			?>
        <section>
            <h1>Software LabelMakerV3 User Guide</h1>
        </section>
        <div class="container">
        <div class="toc">
            <h3>Table of Contents</h3>
            <ul>
                <li><a href="#introduction">1. Introduction</a></li>
                <li><a href="#getting-started">2. Getting Started</a></li>
                <li><a href="#main-navigation">3. Main Navigation</a></li>
                <li><a href="#creating-labels">4. Creating Labels</a></li>
                <li><a href="#no-record-labels">5. No Record Labels</a></li>
                <li><a href="#google-sheets">6. Google Sheets Integration</a></li>
            </ul>
        </div>
        <?php include 'software/introduction.php';
            include 'software/gettingStarted/gettingStarted.php';
            include 'software/mainNavigation/controller.php';
            include 'software/creatingLabels/creatingLabels.php';
            include 'software/noRecordLabels/noRecordLabels.php';
            include 'software/googleSheetIntegration/googleSheetIntegration.php'; ?>
        <a href="?inspections">

    
            <button>
                Click Next
            </button>
        </a>
        <?php
		}
		else if (isset($_GET['inspections'])) {
		?>

        <h1 style="page-break-before:always; ">Inspect, Grade and Sort </h1>
        <h2 tabindex="0">Scan the Tracking Number</h2><img
            src="https://raw.githubusercontent.com/Omar27522/LabelMakerV3/refs/heads/main/HTML/Away%20Products/media/returns.jpg"
            alt="Scan Tracking Number" style="width:15%; float:left;padding-right:3%">
        <img src="https://raw.githubusercontent.com/Omar27522/LabelMakerV3/refs/heads/main/HTML/Away%20Products/media/Create%20New%20Label.jpg"
            alt="Create Label" style="width:30%">
        <h2 style="font-size: 1.9rem;">Use Create Label, and paste it in to iWMS Reverse Inbound Creation, and Receive
        </h2>
        <h2>Label Maker V3</h2>
        <h1 style="page-break-before:always; ">When Return to Sender Always type the SKU.</h1>
        <img src="https://raw.githubusercontent.com/Omar27522/LabelMakerV3/refs/heads/main/HTML/Away%20Products/media/Exceptions.png"
            alt="notes">
        <h2>When Return to Sender Always type the SKU.</h2>
        <h2>Notes:</h2>
        <h2>Search for, or Create Label and Re-box. Receive, Item Info, Container Card, Put Away. Or</h2>
        <h2>Exceptions Received Form, RMA on label but not in system. Sort to Put Away </h2>
        <h1 style="page-break-before:always; ">80%</h1>
        <h2>Brand New</h2>
        <h2>JDL Returns AWAY Grading System</h2>
        <h2><b>Brand New:</b> Usual standard – no defects.</h2>
        <h2><b>Like New:</b> Minor flaws, like a tiny scuff.</h2>
        <h2><b>Very Good:</b> More visible scuffs, but still works perfectly.</h2>
        <h2><b>Not Sellable:</b> Has functional issues.</h2>
        <h2>Returns Department</h2>
        <h2>Not Sellable</h2>
        <h2>Very Good Like New</h2>
        <h2>Recycle Pallets</h2>
        <h1 style="page-break-before:always; ">STEP PLAN</h1>
        <h2>Scan Tracking Number</h2>
        <h2>Inspect, Grade and Sort</h2>
        <h2>Search for, or Create Label and Re-box.</h2>
        <h2>Receive, Item Info, </h2>
        <h2>Container Card, Put Away.</h2>

        <a href="?labeling">
            <button>
                Click Next
            </button>
        </a>
        <?php

		}
		else if (isset($_GET['labeling'])) {
		?>
        <h1>Labeling</h1>
        <h1>Labeling Stuff</h1>
        <h2>A label will be placed on both sides where the pallet jack enters, and this label will include the date the
            items arrived at the warehouse, the number of products on the pallet,and a legend stating that they are
            indeed RETURNS. Then the sorting, cleaning, re-boxing, re-labeling, and grading of the products begin.</h2>
        <img src="https://raw.githubusercontent.com/Omar27522/LabelMakerV3/refs/heads/main/HTML/Away%20Products/media/label.jpg"
            alt="returns" style="padding-right:3%; width:30%; float:right;">
        <img src="https://raw.githubusercontent.com/Omar27522/LabelMakerV3/refs/heads/main/HTML/Away%20Products/media/item_label.png"
            alt="returns" style="padding-right:3%; width:30%; float:right;">

        <a href="?palletizing">
            <button>
                Click Next
            </button>
        </a>
        <?php
		}
		else if (isset($_GET['palletizing'])) {
		?>
        <h1>Palletizing</h1>
        <h1>Team must unload a “returns” truck and account for all returned items. Once the returns are verified, the
            team sorts, cleans, re-boxes, re-labels, and grades the items before putting them away. Our goal is to
            maintain a seamless returns process and uphold the highest standards of quality and organization.
        </h1>
        <section>
            <h2>
                two or more people will help unload it. Two different products arrive, AWAY and non-away. We make sure
                to separate them during the unloading process to avoid mix ups Once everything is unloaded, all tracking
                numbers will be recorded, obtaining the total number of products that arrived, separating them into
                three main categories: RS, Non-RS, and Retail
            </h2>
        </section>

        <aside>
            Once all tracking numbers are recorded, they will be placed in a metal basket to then be transported to the
            returns department. Once they arrive, they will be removed from the baskets and placed on a pallet to be
            wrapped and counted.
        </aside>



        <?php
		}
		else {
	?>


        <section>
            <h1>Welcome to Returns Department at JDL</h1>
        </section>
        <article>
            <h2>Returns Department</h2>
            <ul>
                <li>This is JDL’s returns department. Here, we work with AWAY products only.</li>
                <li>Job Description: AWAY Returns Department at JDL</li>
                <li>We begin by processing any backlog items in the system (items sitting in the warehouse longer than
                    48hrs).</li>
            </ul>
            <h1 style="page-break-before:always; "> <img
                    src="https://www.awaytravel.com/cdn/shop/files/9d673aa3-66f3-4d6c-9590-a133703805f9.jpg" alt="AWAY"
                    width="50%">
                The company focuses on creating high-quality, thoughtfully designed luggage and
                travel accessories that make traveling easier and more enjoyable.</h1>

            <h1 style="page-break-before:always; ">Additionally, AWAY has collaborated with various designers and
                celebrities.
            </h1>

            <aside>
                <h2>AWAY is a modern travel and lifestyle brand that was founded in 2015 by Jen Rubio and Steph Korey.
                    The
                    company
                    focuses on creating high-quality, thoughtfully designed luggage and travel accessories that make
                    traveling easier
                    and more enjoyable.</h2><img
                    src="https://www.awaytravel.com/cdn/shop/files/Business_Travel_Ecomm_Content_Block_New_Arrivals-1.jpg?format=webp&v=1744726849&width=1435"
                    alt="AWAY" width="50%">
                <h2>
                    AWAY is best known for their durable and stylish suitcases, such as the Carry-On, which comes with a
                    built-in
                    battery to charge your devices on the go.
                </h2>
                <h2>100 Day Free Trial</h2>
                <h2>Their products are sold both online and in their retail stores, where customers can experience the
                    brand
                    firsthand. AWAY has a strong commitment to customer satisfaction, offering a 100-day trial period
                    and
                    lifetime
                    warranty on their luggage.</h2>

                <h2>They also emphasize sustainability by using recycled materials and supporting various environmental
                    initiatives.
                </h2>
                <p>limited-edition collections, further appeal to a wide range of travelers. The company's mission:
                    inspire
                    and enable
                    more meaningful travel experiences for people around the world.</p>
            </aside>
            <a href="?dailyTasks">
                <button>
                    Click Next
                </button>
            </a>
        </article>
        <?php } ?>
</body>

</html>