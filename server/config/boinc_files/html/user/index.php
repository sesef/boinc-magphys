<?php
// This file is part of BOINC.
// http://boinc.berkeley.edu
// Copyright (C) 2008 University of California
//
// BOINC is free software; you can redistribute it and/or modify it
// under the terms of the GNU Lesser General Public License
// as published by the Free Software Foundation,
// either version 3 of the License, or (at your option) any later version.
//
// BOINC is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
// See the GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with BOINC.  If not, see <http://www.gnu.org/licenses/>.

// This is a template for your web site's front page.
// You are encouraged to customize this file,
// and to create a graphical identity for your web site
// my developing your own stylesheet
// and customizing the header/footer functions in html/project/project.inc

require_once("../inc/db.inc");
require_once("../inc/util.inc");
require_once("../inc/news.inc");
require_once("../inc/cache.inc");
require_once("../inc/uotd.inc");
require_once("../inc/sanitize_html.inc");
require_once("../inc/text_transform.inc");
require_once("../project/project.inc");

check_get_args(array());

function show_nav() {
    $config = get_config();
    $master_url = parse_config($config, "<master_url>");
    $no_computing = parse_config($config, "<no_computing>");
    $no_web_account_creation = parse_bool($config, "no_web_account_creation");
    $user = get_logged_in_user();
    echo "<div class=\"mainnav\">
        <h2 class=headline>About ".PROJECT."</h2>
    ";
    if ($no_computing) {
        echo "
            theSkyNet POGS is a research project that uses volunteers
            to do research in astronomy.
We will combine the spectral coverage of GALEX, Pan-STARRS1, and WISE to generate a multi-wavelength UV-optical-NIR galaxy atlas for the nearby Universe.
We will measure physical parameters (such as stellar mass surface density, star formation rate surface density, attenuation, and first-order star formation history) on a resolved pixel-by-pixel basis using spectral energy distribution (SED) fitting techniques in a distributed computing mode.
        ";
    } else {
        echo "
            theSkyNet POGS is a research project that uses Internet-connected
            computers to do research in astronomy.
We will combine the spectral coverage of GALEX, Pan-STARRS1, and WISE to generate a multi-wavelength UV-optical-NIR galaxy atlas for the nearby Universe.
We will measure physical parameters (such as stellar mass surface density, star formation rate surface density, attenuation, and first-order star formation history) on a resolved pixel-by-pixel basis using spectral energy distribution (SED) fitting techniques in a distributed computing mode.
            You can participate by downloading and running a free program
            on your computer.
        ";
    }
    echo "
        <p>
        theSkyNet POGS is based at 
        The International Centre for Radio Astronomy Research.
        <ul>
	<li><a href=\"../pogssite/pogs/".$user->id."\">Images you have processed</a>
        <li><a href=\"../pogssite/pogs/GalaxyList?page=1\">Images for all the Galaxies used in the survey</a>
        <li> [Link to page describing your research in detail]
        <li> [Link to page listing project personnel, and an email address]
        </ul>
        <h2 class=headline>Join ".PROJECT."</h2>
        <ul>
    ";
    if ($no_computing) {
        echo "
            <li> <a href=\"create_account_form.php\">Create an account</a>
        ";
    } else {
        echo "
            <li><a href=\"info.php\">".tra("Read our rules and policies")."</a>
            <li> This project uses BOINC.
                If you're already running BOINC, select Add Project.
                If not, <a target=\"_new\" href=\"http://boinc.berkeley.edu/download.php\">download BOINC</a>.
            <li> When prompted, enter <br><b>".$master_url."</b>
        ";
        if (!$no_web_account_creation) {
            echo "
                <li> If you're running a command-line version of BOINC,
                    <a href=\"create_account_form.php\">create an account</a> first.
            ";
        }
        echo "
            <li> If you have any problems,
                <a target=\"_new\" href=\"http://boinc.berkeley.edu/wiki/BOINC_Help\">get help here</a>.
        ";
    }
    echo "
        </ul>

        <h2 class=headline>Returning participants</h2>
        <ul>
    ";
    if ($no_computing) {
        echo "
            <li><a href=\"bossa_apps.php\">Do work</a>
            <li><a href=\"home.php\">Your account</a> - view stats, modify preferences
            <li><a href=\"team.php\">Teams</a> - create or join a team
        ";
    } else {
        echo "
            <li><a href=\"home.php\">Your account</a> - view stats, modify preferences
            <li><a href=server_status.php>Server status</a>
            <li><a href=\"team.php\">Teams</a> - create or join a team
            <li><a href=\"cert1.php\">Certificate</a>
            <li><a href=\"apps.php\">".tra("Applications")."</a>
        ";
    }
    echo "
        </ul>
        <h2 class=headline>".tra("Community")."</h2>
        <ul>
        <li><a href=\"profile_menu.php\">".tra("Profiles")."</a>
        <li><a href=\"user_search.php\">User search</a>
        <li><a href=\"forum_index.php\">".tra("Message boards")."</a>
        <li><a href=\"forum_help_desk.php\">".tra("Questions and Answers")."</a>
        <li><a href=\"stats.php\">Statistics</a>
        <li><a href=language_select.php>Languages</a>
        </ul>
        </div>
    ";
}

$stopped = web_stopped();
$rssname = PROJECT . " RSS 2.0" ;
$rsslink = URL_BASE . "rss_main.php";

header("Content-type: text/html; charset=utf-8");

echo "<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\">";

echo "<html>
    <head>
    <title>".PROJECT."</title>
    <link rel=\"stylesheet\" type=\"text/css\" href=\"main.css\" media=\"all\" />
    <link rel=\"stylesheet\" type=\"text/css\" href=\"".STYLESHEET."\">
    <link rel=\"alternate\" type=\"application/rss+xml\" title=\"".$rssname."\" href=\"".$rsslink."\">
";
include 'schedulers.txt';
echo "
    </head><body>
<div id=\"fb-root\"></div>
<script>(function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = \"//connect.facebook.net/en_US/all.js#xfbml=1\";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));</script>
    <div class=page_title>".PROJECT."</div>
    <div><img src=\"logos/POGSbanner_label.jpg\" alt=\"POGS Banner\" width=\"808\" height=\"202\" border=\"0\" usemap=\"#map\" />
        <map name=\"map\">
            <area shape=\"rect\" coords=\"0,0,200,200\" alt=\"GALEX (Galaxy Evolution Explorer)\" href=\"http://www.galex.caltech.edu\" />
            <area shape=\"rect\" coords=\"203,0,403,200\" alt=\"Pan-STARRS1\" href=\"http://www.ps1sc.org\" />
            <area shape=\"rect\" coords=\"406,0,606,200\" alt=\"WISE (Wide-field Infrared Survey Explorer)\" href=\"http://wise.ssl.berkeley.edu/index.html\" />
            <area shape=\"rect\" coords=\"608,0,808,200\" alt=\"MAGPHYS\" href=\"http://www.iap.fr/magphys/magphys/MAGPHYS.html\" />
        </map>
   </div>
";

if (!$stopped) {
    get_logged_in_user(false);
    show_login_info();
}

echo "
    <table cellpadding=\"8\" cellspacing=\"4\" class=bordered>
    <tr><td rowspan=\"2\" valign=\"top\" width=\"40%\">
";

if ($stopped) {
    echo "
        <b>".PROJECT." is temporarily shut down for maintenance.
        Please try again later</b>.
    ";
} else {
    db_init();
    show_nav();
}

echo "
    <p>
    <a href=\"http://boinc.berkeley.edu/\"><img align=\"middle\" border=\"0\" src=\"img/pb_boinc.gif\" alt=\"Powered by BOINC\"></a>
    </p>
    <div class=\"fb-like\" data-href=\"http://ec2-23-23-126-96.compute-1.amazonaws.com/pogs\" data-send=\"false\" data-width=\"450\" data-show-faces=\"false\"></div>
    </td>
";

if (!$stopped) {
    $profile = get_current_uotd();
    if ($profile) {
        echo "
            <td class=uotd>
            <h2 class=headline>".tra("User of the day")."</h2>
        ";
        show_uotd($profile);
        echo "</td></tr>\n";
    }
}

echo "
    <tr><td class=news>
    <h2 class=headline>News</h2>
    <p>
";
include("motd.php");
show_news(0, 5);
echo "
    </td>
    </tr></table>
";

page_tail_main();

?>
