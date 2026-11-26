---
title: "Drawingpad"
source: "https://www.livingneighborhoods.org/drawing-pad/drawingpad.htm"
archive_path: "archive/www.livingneighborhoods.org/drawing-pad/drawingpad.htm"
source_sha256: "45452f18cd268de6a5c1a5c6d1a513dd4b289dcc67cf2bb6b6f03fdb610c675e"
frames: ["wizard.htm"]
---

<div id="windowRegion" class="regiona">

<div class="regionb">

<span class="regionTitle">Current\
 Project</span>

<div class="regionc">

|  |
|----|
| <span id="fileName" class="h6" style="color:ff0000;font-weight:bold;">DEMO</span> |

|  |
|----|
| <span id="projectName" class="h6" style="color:ff0000;font-weight:bold;">project name</span> |

</div>

</div>

</div>

<div id="stepRegion" class="regiona">

<span style="color:red;font-size:12px;font-family:arial;">**Caution. DEMO ONLY. This part of the website is not yet working properly. You can play with it, and see what it can soon bring you, but it is not yet ready for serious use.\**
</span>\

<span style="color:FFFFDD;font-size:12px;font-family:arial;">**To edit the step list right click the steps or the layer. This will give you options that allow you to edit the list, rename them, create them, and move items,\**
</span>

</div>

<div id="buttonRegion" style="position:absolute;top:100;left:140;z-index:10">

|  |
|:---|
| <img src="buttons/lynx-hand.jpg" class="buttonInactive" data-border="1" onmouseover="activityButtonMouse(this,&quot;over&quot;)" onmouseout="activityButtonMouse(this,&quot;out&quot;)" onmousedown="activityButtonMouse(this,&quot;down&quot;)" onmouseup="activityButtonMouse(this,&quot;up&quot;)" onclick="activityButtonClicked(this,&quot;pan&quot;)" width="31" height="31" alt="move drawing across the screen" /> <img src="buttons/lynx-zoomplus.jpg" id="zoom_in_button" class="button" data-border="1" onmouseover="lndMouseOverButton(this,true)" onmousedown="lndButtonDepressed(this,true)" onmouseup="lndButtonDepressed(this,false)" onmouseout="lndMouseOverButton(this,false)" onclick="document.all.lndraw_applet.zoomIn()" width="31" height="31" alt="zoom + to enlarge" /> <img src="buttons/lynx-zoomminus.jpg" id="zoom_out_button" class="button" data-border="1" onmouseover="lndMouseOverButton(this,true)" onmousedown="lndButtonDepressed(this,true)" onmouseup="lndButtonDepressed(this,false)" onmouseout="lndMouseOverButton(this,false)" onclick="document.all.lndraw_applet.zoomOut()" width="31" height="31" alt="zoom + to enlarge" />    <img src="buttons/lynx-color2.jpg" data-border="1" onclick="document.all.lndraw_applet.chooseAColor()" width="31" height="31" alt="select color for pen or fill or text" /> <img src="buttons/color-light-whitering4.gif" id="penColorSwatch" data-border="1" height="31" alt="this is the currently selected color" /> <img src="buttons/lynx-thickness.jpg" data-border="1" onclick="document.all.lndraw_applet.setLineThickness()" width="31" height="31" alt="set line thickness" />    <img src="buttons/lynx-pencil2.jpg" class="buttonInactive" data-border="1" onmouseover="activityButtonMouse(this,&quot;over&quot;)" onmouseout="activityButtonMouse(this,&quot;out&quot;)" onmousedown="activityButtonMouse(this,&quot;down&quot;)" onmouseup="activityButtonMouse(this,&quot;up&quot;)" onclick="activityButtonClicked(this,&quot;pen&quot;)" width="28" height="28" alt="start to draw" /> <img src="buttons/lynx-lasso.jpg" class="buttonInactive" data-border="1" onmouseover="activityButtonMouse(this,&quot;over&quot;)" onmouseout="activityButtonMouse(this,&quot;out&quot;)" onmousedown="activityButtonMouse(this,&quot;down&quot;)" onmouseup="activityButtonMouse(this,&quot;up&quot;)" onclick="activityButtonClicked(this,&quot;lasso&quot;)" width="28" height="28" alt="fill with selected color" /> <img src="buttons/text-button.jpg" data-border="1" width="31" height="31" alt="type statement at cursor" /> <img src="buttons/lynx-erase.jpg" class="buttonInactive" data-border="1" onmouseover="activityButtonMouse(this,&quot;over&quot;)" onmouseout="activityButtonMouse(this,&quot;out&quot;)" onmousedown="activityButtonMouse(this,&quot;down&quot;)" onmouseup="activityButtonMouse(this,&quot;up&quot;)" onclick="activityButtonClicked(this,&quot;eraser&quot;)" width="28" height="28" alt="erase" /> <img src="buttons/positive-space.jpg" data-border="1" width="31" height="31" alt="check and repair positive space in the selected area" />    <img src="buttons/lynx-undo.jpg" data-border="1" onclick="document.all.lndraw_applet.undo()" width="31" height="31" alt="undo the previous act" /> <img src="buttons/lynx-redo.jpg" data-border="1" onclick="document.all.lndraw_applet.redo()" width="31" height="31" alt="redo the undo" />      |

</div>

<div style="position:absolute;top:600;left:0">

</div>

<div id="statusBar" class="regiona">

|  |  |  |  |  |
|----|----|----|----|----|
| <span class="h6class" style="color:ffffdd">project</span> | <span class="h6class" style="color:ffffdd">project file</span> | <span class="h6class" style="color:ffffdd">selected step</span> | <span class="h6class" style="color:ffffdd">selected layer</span> | <span class="h6class" style="color:ffffdd">current map width in feet</span> |

</div>

<div id="appletRegion" style="position:absolute">

</div>

<div id="stepname" style="position:absolute;top:0;left:140;bgcolor:#005544;visibility:visible;">

</div>

<div id="basemap">

<span class="h6bold" style="font-size:14px">BASEMAP   First find an aerial photograph of the area where the future neighborhood will be. You can get it from many sources, save it as a jpg in your file for the project. It is the reality of this photograph, with trees, water, roads, buildings, that will make it possible to conceive a place that grows naturally from the details of the land itself.</span>

</div>

<div id="basemapcorrections">

<span class="h6bold" style="font-size:14px">BASEMAP CORRECTIONS   Now improve the detail of the background map to include details and dimensions that are important, or that will be important to have in exactly the right place during the unfolding. You can draw this on a separate layer, and continue to improve these details, while your overall process goes forward.</span>

</div>

<div id="diagnosis">

<span class="h6bold" style="font-size:14px">DIAGNOSIS   Now look for places, all over the neighborhood area, where beautiful things need to be protected and enhanced, and bad places where improvements need to be made. Draw these in, on this map layer. The places you identify and draw on the maplayer, should be in the following categories:\
</span>

Beautiful views, which give you pleasure standing there.

Spots that are inherently lovely, or fun, or pleasant, which should be protected and enhanced.

Places where latent centers exist, that have the potential for being made more beautiful.

</div>

<div id="wholeness">

<span class="h6bold" style="font-size:14px">WHOLENESS   Try to make a diagram which captures the most important pattern or wholeness of the place: a structure which comes from that place, is of that place, and embraces the whole extent of the neighborhood.</span>

</div>

<div id="maincenter">

<span class="h6bold" style="font-size:14px">MAIN CENTER   Find the main center of the neighborhood: that place in the land, or among the existing built places, which is the most natural and magnetic center, which will have the quality that people in the neighborhood will be drawn to it, and without thinking, will go there all the time.</span>

</div>

<style>
#textRegion {position:absolute;left:130;top:0;width:700;height:85;background-color:#005544;color:#ffff77;padding-left:5px;padding-top:3px;padding-bottom:3px;padding-right:4px;font-weight:bold;font-size:15px;font-family:arial}

#stepname {position:absolute;left:0;top:700;width:700;height:85;background-color:#005544;color:#ffff77;padding-left:5px;padding-top:3px;padding-bottom:3px;padding-right:4px;font-weight:bold;font-size:15px;font-family:arial}

#basemap {position:absolute;left:130;top:0;width:700;height:85;background-color:#005544;color:#ffff77;padding-left:4px;padding-top:3px;padding-bottom:3px;padding-right:4px;visibility:hidden;}

#basemapcorrections {position:absolute;left:130;top:0;width:700;height:85;background-color:#005544;color:#ffff77;padding-left:4px;padding-top:3px;padding-bottom:3px;padding-right:4px;visibility:hidden;}

#diagnosis {position:absolute;left:130;top:0;width:700;height:85;background-color:#005544;color:#ffff77;padding-left:4px;padding-top:3px;padding-bottom:3px;padding-right:4px;visibility:hidden;}

#wholeness {position:absolute;left:130;top:0;width:700;height:85;background-color:#005544;color:#ffff77;padding-left:4px;padding-top:3px;padding-bottom:3px;padding-right:4px;visibility:hidden;}

#maincenter {position:absolute;left:130;top:0;width:700;height:85;background-color:#005544;color:#ffff77;padding-left:4px;padding-top:3px;padding-bottom:3px;padding-right:4px;visibility:hidden;}

#startinstructions {position:absolute;left:130;top:150;width:700;height:450;background-color:#ffffff;color:#000000;padding-left:4px;padding-top:4px;padding-bottom:3px;padding-right:4px;visibility:visible;}

<!-- <TR><td width=70 align=left valign=bottom bgcolor=005544><span class=h6bold><a href="javascript:void(0)"     
onmouseover="changeState('startInstructions','visible');  changeState('appletRegion','hidden');" onmouseout="changeState('startInstructions','hidden');changeState('appletRegion','visible');" >
<SPAN onmouseover = "changeClass(this,'highlight')" class=h6bold style=bgcolor:red;>Start Instructions</span></td> -->


<!-- <td width=110 align=left valign=bottom bgcolor=ccccff><span class=h7>Map corrections layer</span></td><td width=20 align=left valign=bottom bgcolor=005544><img src=buttons/no-eye5.jpg height=18 valign=bottom></td></tr> -->

</style>
