#!/bin/bash

mkdir artwork-german
cd artwork-german

# Grundkarten - Geld- und Punktekarten, Fluch
wget http://www.dominionblog.de/wp-content/uploads/2009/07/7Kupfer.png -O copper.png
convert copper.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 copper.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/14Silber.png -O silver.png
convert silver.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 silver.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/21Gold.png -O gold.png
convert gold.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 gold.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/17Anwesen.png -O estate.png
convert estate.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 estate.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/19Herzogtum.png -O duchy.png
convert duchy.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 duchy.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/12Provinz.png -O province.png
convert province.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 province.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/Fluch.jpg -O curse.jpg

rm *.png

# Basisspiel
wget http://www.dominionblog.de/wp-content/uploads/2009/06/Abenteurer.png -O adventurer.png
convert adventurer.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 adventurer.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/18Bibo.png -O library.png
convert library.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 library.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/20Burggraben.png -O moat.png
convert moat.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 moat.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/5B%C3%BCrokrat.png -O bureaucrat.png
convert bureaucrat.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 bureaucrat.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/06/Dieb.png -O thief.png
convert thief.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 thief.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/06/Dorf2.png -O village.png
convert village.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 village.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/24Festmahl.png -O feast.png
convert feast.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 feast.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/Geldverleiher.jpg -O moneylender.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/23G%C3%A4rten.png -O gardens.png
convert gardens.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 gardens.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/06/Hexe1.png -O witch.png
convert witch.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 witch.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/Holzf%C3%A4ller.jpg -O woodcutter.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/06/Jahrmarkt.png -O festival.png
convert festival.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 festival.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/22Kanzler.png -O chancellor.png
convert chancellor.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 chancellor.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/3Kapelle.png -O chapel.png
convert chapel.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 chapel.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/4Keller.png -O cellar.png
convert cellar.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 cellar.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/6Lab.png -O laboratory.png
convert laboratory.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 laboratory.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/9Markt.png -O market.png
convert market.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 market.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/8Miliz.png -O militia.png
convert militia.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 militia.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/10Mine.png -O mine.png
convert mine.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 mine.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/11Ratsversammlung.png -O councilroom.png
convert councilroom.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 councilroom.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/13Schmiede.png -O smithy.png
convert smithy.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 smithy.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/2Spion.png -O spy.png
convert spy.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 spy.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/1Thronsaal.png -O throneroom.png
convert throneroom.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 throneroom.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/15Umbau.png -O remodel.png
convert remodel.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 remodel.jpg
wget http://www.dominionblog.de/wp-content/uploads/2009/07/16Werkstatt.png -O workshop.png
convert workshop.png -gravity North -chop 0x15  -gravity South -chop 0x10 -gravity West -chop 20x0 -gravity East -chop 20x0 workshop.jpg

rm *.png

# Intrige
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_adelige.jpg -O nobles.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_anbau.jpg -O upgrade.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_armenviertel.jpg -O shantytown.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_baron.jpg -O baron.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_bergwerk.jpg -O miningvillage.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_bruecke.jpg -O bridge.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_burghof.jpg -O courtyard.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_eisenhuette.jpg -O ironworks.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_geheimkammer.jpg -O secretchamber.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_grosse_halle.jpg -O greathall.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_handelsposten.jpg -O tradingpost.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_handlanger.jpg -O pawn.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_harem.jpg -O harem.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_herzog.jpg -O duke.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_kerkermeister.jpg -O torturer.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_kupferschmied.jpg -O coppersmith.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_lakai.jpg -O minion.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_maskerade.jpg -O masquerade.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_saboteur.jpg -O saboteur.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_spaeher.jpg -O scout.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_tribut.jpg -O tribute.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_trickser.jpg -O swindler.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_verschwoerer.jpg -O conspirator.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_verwalter.jpg -O steward.jpg
wget http://www.brettspiele-report.de/images/dominion/die_intrige/dominion_die_intrige_spielkarte_wunschbrunnen.jpg -O wishingwell.jpg

# Seaside
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_ausguck.jpg -O lookout.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_aussenposten.jpg -O outpost.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_bazar.jpg -O bazaar.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_beutelschneider.jpg -O cutpurse.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_botschafter.jpg -O ambassador.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_eingeborenendorf.jpg -O nativevillage.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_embargo.jpg -O embargo.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_entdecker.jpg -O explorer.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_fischerdorf.jpg -O fishingvillage.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_geisterschiff.jpg -O ghostship.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_hafen.jpg -O haven.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_handelsschiff.jpg -O merchantship.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_insel.jpg -O island.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_karawane.jpg -O caravan.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_lagerhaus.jpg -O warehouse.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_leuchtturm.jpg -O lighthouse.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_muellverwerter.jpg -O salvager.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_navigator.jpg -O navigator.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_perlentaucher.jpg -O pearldiver.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_piratenschiff.jpg -O pirateship.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_schatzkammer.jpg -O treasury.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_schatzkarte.jpg -O treasuremap.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_schmuggler.jpg -O smugglers.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_seehexe.jpg -O seahag.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_taktiker.jpg -O tactician.jpg
wget http://www.brettspiele-report.de/images/dominion/seaside/dominion_seaside_spielkarte_werft.jpg -O wharf.jpg

#wget http://www.dominionblog.de/wp-content/uploads/2009/10/Ausguck.jpg -O lookout.jpg
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200Aussen.png -O outpost.png
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/Bazar.jpg -O bazaar.jpg
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200Beutel.png -O cutpurse.png
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200Botschafter.png -O ambassador.png
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200Eingeborenen.png -O nativevillage.png
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200Embargo.png -O embargo.png
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200Entdecker.png -O explorer.png
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200Fischerdorf.png -O fishingvillage.png
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200Geister.png -O ghostship.png
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/Hafen.jpg -O haven.jpg
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200Hafen.png -O merchantship.png
## -------- beschneiden ?
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/Island-Insel2.jpg -O island.jpg
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200Karawane.png -O caravan.png
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200Lagerhaus.png -O warehouse.png
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/Leuchtturm.jpg -O lighthouse.jpg
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200M%C3%BCll.png -O salvager.png
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200Navigator.png -O navigator.png
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200Perlen.png -O pearldiver.png
# --------- eigentlich zu klein zum lesen
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200Piraten.png -O pirateship.png
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/Schatzkammer.jpg -O treasury.jpg
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200Schatzkarte.png -O treasuremap.png
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200Schmuggler.png -O smugglers.png
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200See.png -O seahag.png
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200Taktiker.png -O tactician.png
#wget http://www.dominionblog.de/wp-content/uploads/2009/10/200Werft.png -O wharf.png

# Alchimisten
wget http://www.brettspiele-report.de/images/dominion/die_alchemisten/dominion_die_alchemisten_spielkarte_alchemist.jpg -O alchemist.jpg
wget http://www.brettspiele-report.de/images/dominion/die_alchemisten/dominion_die_alchemisten_spielkarte_apotheker.jpg -O apothecary.jpg
wget http://www.brettspiele-report.de/images/dominion/die_alchemisten/dominion_die_alchemisten_spielkarte_besessenheit.jpg -O possession.jpg
wget http://www.brettspiele-report.de/images/dominion/die_alchemisten/dominion_die_alchemisten_spielkarte_golem.jpg -O golem.jpg
wget http://www.brettspiele-report.de/images/dominion/die_alchemisten/dominion_die_alchemisten_spielkarte_kraeuterkundiger.jpg -O herbalist.jpg
wget http://www.brettspiele-report.de/images/dominion/die_alchemisten/dominion_die_alchemisten_spielkarte_lehrling.jpg -O apprentice.jpg
wget http://www.brettspiele-report.de/images/dominion/die_alchemisten/dominion_die_alchemisten_spielkarte_stein_der_weisen.jpg -O philosophersstone.jpg
wget http://www.brettspiele-report.de/images/dominion/die_alchemisten/dominion_die_alchemisten_spielkarte_trank.jpg -O potion.jpg
wget http://www.brettspiele-report.de/images/dominion/die_alchemisten/dominion_die_alchemisten_spielkarte_universitaet.jpg -O university.jpg
wget http://www.brettspiele-report.de/images/dominion/die_alchemisten/dominion_die_alchemisten_spielkarte_vertrauter.jpg -O familiar.jpg
wget http://www.brettspiele-report.de/images/dominion/die_alchemisten/dominion_die_alchemisten_spielkarte_verwandlung.jpg -O transmute.jpg
wget http://www.brettspiele-report.de/images/dominion/die_alchemisten/dominion_die_alchemisten_spielkarte_vision.jpg -O scryingpool.jpg
wget http://www.brettspiele-report.de/images/dominion/die_alchemisten/dominion_die_alchemisten_spielkarte_weinberg.jpg -O vineyard.jpg
# http://www.dominionblog.de/wp-content/uploads/2010/04/Alchemist.png
# http://www.dominionblog.de/wp-content/uploads/2010/04/Apotheker.png
# http://www.dominionblog.de/wp-content/uploads/2010/04/Besessenheit.png

# Reiche Ernte - Cornucopia
wget http://www.dominionblog.de/wp-content/uploads/2011/04/Bauerndorf.png -O farmingvillage.png
wget http://www.dominionblog.de/wp-content/uploads/2011/04/Ernte.png -O harvest.png
wget http://www.dominionblog.de/wp-content/uploads/2011/06/Festplatz.png -O fairgrounds.png
wget http://www.dominionblog.de/wp-content/uploads/2011/04/F%C3%BCllhorn.png -O hornofplenty.png
wget http://www.dominionblog.de/wp-content/uploads/2011/06/harlekin.png -O jester.png
wget http://www.dominionblog.de/wp-content/uploads/2011/06/jagdgesellschaft.png -O huntingparty.png
wget http://www.dominionblog.de/wp-content/uploads/2011/06/jungehexe.png -O youngwitch.png
wget http://www.dominionblog.de/wp-content/uploads/2011/06/Menagerie.png -O menagerie.png
wget http://www.dominionblog.de/wp-content/uploads/2011/06/Nachbau.png -O remake.png
wget http://www.dominionblog.de/wp-content/uploads/2011/06/Pferdeh%C3%A4ndler.png -O horsetraders.png
wget http://www.dominionblog.de/wp-content/uploads/2011/06/Turnier.png -O tournament.png
wget http://www.dominionblog.de/wp-content/uploads/2011/04/Wahrsagerin.png -O fortuneteller.png
wget http://www.dominionblog.de/wp-content/uploads/2011/04/Weiler.png -O hamlet.png
# Es fehlen die Preise des Turniers:
# "Prinzessin", "Diadem", "Ein Sack voll Gold", "Gefolge", "Streitross"
wget http://www8.pic-upload.de/03.06.11/2z1irqq1348.jpg
# Streitross
convert 2z1irqq1348.jpg -gravity North -chop 0x626  -gravity South -chop 0x4 -gravity West -chop 744x0 -gravity East -chop 450x0 trustysteed.jpg
# Gefolge
convert 2z1irqq1348.jpg -gravity North -chop 0x605  -gravity South -chop 0x8 -gravity West -chop 365x0 -gravity East -chop 830x0 followers.jpg
# Ein Sack voll Gold
convert -rotate -2 2z1irqq1348.jpg 2z1irqq1348.png
convert 2z1irqq1348.png -gravity North -chop 0x82  -gravity South -chop 0x594 -gravity West -chop 228x0 -gravity East -chop 1010x0 bagofgold.jpg
# Diadem
convert -rotate -3 2z1irqq1348.jpg 2z1irqq1348.png
convert 2z1irqq1348.png -gravity North -chop 0x117  -gravity South -chop 0x611 -gravity West -chop 603x0 -gravity East -chop 660x0 diadem.jpg
# Prinzessin
convert 2z1irqq1348.png -gravity North -chop 0x104  -gravity South -chop 0x630 -gravity West -chop 977x0 -gravity East -chop 280x0 princess.jpg
rm 2z1irqq1348.jpg 2z1irqq1348.png

# Blütezeit - Prosperity
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_abenteurer.jpg -O venture.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_arbeiterdorf.jpg -O workersvillage.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_ausbau.jpg -O expand.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_bank.jpg -O bank.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_bischof.jpg -O bishop.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_denkmal.jpg -O monument.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_gesindel.jpg -O rabble.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_gewoelbe.jpg -O vault.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_grosser_markt.jpg -O grandmarket.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_halsabschneider.jpg -O goons.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_handelsroute.jpg -O traderoute.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_hausierer.jpg -O peddler.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_hort.jpg -O hoard.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_koenigliches_siegel.jpg -O royalseal.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_koenigshof.jpg -O kingscourt.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_kolonie.jpg -O colony.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_kunstschmiede.jpg -O forge.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_leihhaus.jpg -O countinghouse.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_lohn.jpg -O loan.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_muenzer.jpg -O mint.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_platin.jpg -O platinum.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_quacksalber.jpg -O mountebank.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_schmuggelware.jpg -O contraband.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_stadt.jpg -O city.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_steinbruch.jpg -O quarry.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_talisman.jpg -O talisman.jpg
wget http://www.brettspiele-report.de/images/dominion/bluetezeit/dominion_bluetezeit_spielkarte_wachturm.jpg -O watchtower.jpg

# Hinterland
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Aufbau.png -O develop.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Blutzoll.png -O illgottengains.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Botschaft.png -O embassy.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/EdlerR%C3%A4uber.png -O noblebrigand.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Fahrender-H%C3%A4ndler.png -O trader.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Feilscher.png -O haggler.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Fernstra%C3%9Fe.png -O highway.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Fruchtbares-Land.png -O farmland.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Gasthaus.png -O inn.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Gew%C3%BCrzh%C3%A4ndler.png -O spicemerchant.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Grenzdorf.png -O bordervillage.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Herzogin.png -O duchess.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Kartograph.png -O cartographer.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Katzengold1.png -O foolsgold.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Komplott.png -O scheme.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Lebensk%C3%BCnstler.png -O jackofalltrades.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Mandarin.png -O mandarin.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Markgraf.png -O margrave.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Nomadencamp.png -O nomadcamp.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Oase.png -O oasis.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Orakel.png -O oracle.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Schatztruhe.png -O cache.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Seidenstrasse.png -O silkroad.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Stallungen.png -O stables.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Tunnel.png -O tunnel.png
wget http://www.dominionblog.de/wp-content/uploads/2011/10/Wegkreuzung.png -O crossroads.png


# Promo Gesandter
wget http://www.dominionblog.de/wp-content/uploads/2009/07/Gesandter.jpg -O envoy.jpg
# Promo Gouverneur
wget http://de.trictrac.net/medias/images/1330096596.1bbeeqU.jpg -O governor.jpg
# Promo Geldversteck
wget http://www.dominionblog.de/wp-content/uploads/2010/02/Geldversteck_vorne.png -O stash.jpg
# Promo Carcassonne
wget http://cf.geekdo-images.com/images/pic1247084_lg.jpg -O walledvillage.jpg
# Promo Schwarzmarkt
wget http://www.ludopedia.de/images/thumb/4/4b/Dominion_Schwarzmarkt.jpg/385px-Dominion_Schwarzmarkt.jpg -O blackmarket.jpg

find . -type f -name "*.png" | while read image; do nur_image=$(basename $image);
convert -quality 90 $nur_image ${nur_image//.png/.jpg}; done

rm *.png

cd ..
find artwork-german/ -type f -name "*.jpg" -exec mv {} res/cards_full/ \;
rmdir artwork-german
