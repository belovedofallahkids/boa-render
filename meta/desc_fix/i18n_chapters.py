# Localized chapters + sources for all 16 episodes (owner request 14.11.2026)
# Times = live German description (verified in Studio 14.11.2026). Dubs follow German timing.
import json

HDR = {'ar': '⏱️ الفصول', 'en': '⏱️ Chapters', 'fr': '⏱️ Chapitres', 'tr': '⏱️ Bölümler', 'bs': '⏱️ Poglavlja', 'sq': '⏱️ Kapitujt'}
SRC = {'ar': 'المصادر: القرآن الكريم', 'en': 'Sources: Quran', 'fr': 'Sources : Coran', 'tr': "Kaynaklar: Kur'an", 'bs': "Izvori: Kur'an", 'sq': 'Burimet: Kurani'}
HAD_AR = {'Sahih al-Bukhari': 'صحيح البخاري', 'Sahih Muslim': 'صحيح مسلم', 'Sunan at-Tirmidhi': 'سنن الترمذي',
          'Sahih Ibn Hibban': 'صحيح ابن حبان', 'Sunan Ibn Majah': 'سنن ابن ماجه'}

# id, times, quran refs, hadith list, chapters per language (same order as times)
EP = [
 dict(n='01', id='OXgZKt6u8Jo', t=['0:00','0:28','1:14','1:59','3:11','4:06','5:23'], q='2:30–38, 7:11–25, 15:26–43, 20:115–123, 38:71–85', h=[],
  ar=['من هو أول إنسان؟','الله يخلق آدم من طين','الله يعلّم آدم الأسماء كلها','الملائكة تسجد – وإبليس يتكبّر','في الجنة والشجرة الممنوعة','التوبة والمغفرة والحياة على الأرض','تصبحون على خير – عبرة القصة'],
  en=['Who was the very first human?','Allah creates Adam from clay','Allah teaches Adam the names of all things','The angels bow down – Iblis is arrogant','In Paradise and the forbidden tree','Repentance, forgiveness and life on Earth','Good night – the lesson of the story'],
  fr=['Qui fut le tout premier humain ?','Allah crée Adam d’argile','Allah enseigne à Adam le nom de toute chose','Les anges se prosternent – Iblis s’enorgueillit','Au Paradis et l’arbre interdit','Repentir, pardon et vie sur Terre','Bonne nuit – la leçon de l’histoire'],
  tr=['İlk insan kimdi?','Allah Âdem’i çamurdan yaratıyor','Allah Âdem’e bütün isimleri öğretiyor','Melekler secde ediyor – İblis büyükleniyor','Cennette ve yasak ağaç','Tövbe, bağışlanma ve yeryüzünde hayat','İyi geceler – hikâyenin dersi'],
  bs=['Ko je bio prvi čovjek?','Allah stvara Adema od ilovače','Allah uči Adema imenima svih stvari','Meleki se klanjaju – Iblis se uzoholio','U Džennetu i zabranjeno drvo','Pokajanje, oprost i život na Zemlji','Laku noć – pouka priče'],
  sq=['Kush ishte njeriu i parë?','Allahu e krijon Ademin prej balte','Allahu ia mëson Ademit emrat e të gjitha gjërave','Engjëjt bien në sexhde – Iblisi mendjemadhësohet','Në Xhenet dhe pema e ndaluar','Pendimi, falja dhe jeta në Tokë','Natën e mirë – mësimi i tregimit']),
 dict(n='02', id='8aFWSLdqUAE', t=['0:00','0:32','1:10','1:41','2:21','2:43','3:08'], q='19:56–57, 21:85–86', h=['Sahih al-Bukhari 3207','Sahih Muslim 162'],
  ar=['أي نبي رُفع مكانًا عليًّا؟','إدريس صدّيق نبي','إدريس من الصابرين والصالحين','رُفع مكانًا عليًّا','السلام في السماء الرابعة','ما نعرفه عن إدريس','تصبحون على خير – عبرة القصة'],
  en=['Which prophet was raised up high?','Idris – a man of truth','Idris was patient and righteous','Raised to a high place','The greeting in the fourth heaven','What we know about Idris','Good night – the lesson of the story'],
  fr=['Quel prophète fut élevé très haut ?','Idris – un homme de vérité','Idris était patient et vertueux','Élevé à un rang sublime','La salutation au quatrième ciel','Ce que nous savons d’Idris','Bonne nuit – la leçon de l’histoire'],
  tr=['Hangi peygamber yücelere kaldırıldı?','İdris – sözü doğru bir insan','İdris sabırlı ve salihti','Yüce bir mekâna kaldırıldı','Dördüncü kat semada selam','İdris hakkında bildiklerimiz','İyi geceler – hikâyenin dersi'],
  bs=['Koji je vjerovjesnik uzdignut visoko?','Idris – čovjek istine','Idris je bio strpljiv i dobar','Uzdignut na visoko mjesto','Selam na četvrtom nebu','Šta znamo o Idrisu','Laku noć – pouka priče'],
  sq=['Cili pejgamber u ngrit lart?','Idrisi – njeri i së vërtetës','Idrisi ishte i durueshëm dhe i mirë','I ngritur në një vend të lartë','Përshëndetja në qiellin e katërt','Çfarë dimë për Idrisin','Natën e mirë – mësimi i tregimit']),
 dict(n='03', id='mCiK-z7qkb8', t=['0:00','0:29','1:00','1:52','2:32','3:10','3:26','4:21','5:00'], q='7:59–64, 11:25–49, 23:23–30, 26:105–122, 29:14–15, 54:9–15, 71:1–28', h=[],
  ar=['سفينة على اليابسة؟','الناس ينسون الله','نوح يدعو قومه','نوح يبني السفينة','الجميع يركبون السفينة','موج كالجبال','نوح ينادي ابنه','الماء يغيض – بداية جديدة','تصبحون على خير – عبرة القصة'],
  en=['A ship on dry land?','People forget Allah','Prophet Noah calls his people','Noah builds the ark','Everyone boards the ark','Waves like mountains','Noah calls his son','The water sinks – a new beginning','Good night – the lesson of the story'],
  fr=['Un bateau sur la terre ferme ?','Les gens oublient Allah','Le prophète Noé appelle son peuple','Noé construit l’arche','Tout le monde monte dans l’arche','Des vagues comme des montagnes','Noé appelle son fils','L’eau se retire – un nouveau départ','Bonne nuit – la leçon de l’histoire'],
  tr=['Kuru toprakta bir gemi mi?','İnsanlar Allah’ı unutuyor','Nuh kavmini çağırıyor','Nuh gemiyi yapıyor','Herkes gemiye biniyor','Dağlar gibi dalgalar','Nuh oğlunu çağırıyor','Sular çekiliyor – yeni bir başlangıç','İyi geceler – hikâyenin dersi'],
  bs=['Brod na suhom kopnu?','Ljudi zaboravljaju Allaha','Nuh poziva svoj narod','Nuh gradi lađu','Svi ulaze u lađu','Talasi kao planine','Nuh doziva svog sina','Voda se povlači – novi početak','Laku noć – pouka priče'],
  sq=['Një anije në tokë të thatë?','Njerëzit e harrojnë Allahun','Nuhu thërret popullin e tij','Nuhu ndërton anijen','Të gjithë hipin në anije','Valë si male','Nuhu thërret djalin e tij','Uji tërhiqet – një fillim i ri','Natën e mirë – mësimi i tregimit']),
 dict(n='04', id='uxD2lZZ1cbU', t=['0:00','0:27','1:00','1:45','2:15','2:53','3:31','3:51'], q='7:65–72, 11:50–60, 26:123–140, 41:15–16, 46:21–25, 69:6–8, 89:6–8', h=[],
  ar=['ما الأقوى من أقوى الناس؟','قوم عاد ومدينة إرم','الكِبر بدل الشكر','هود يدعو قومه إلى الله','هود يتوكل على الله','السحابة السوداء والريح','الله ينجّي هودًا والمؤمنين','تصبحون على خير – عبرة القصة'],
  en=['What is stronger than the strongest people?','The people of Ad and the city of Iram','Pride instead of thankfulness','Prophet Hud calls his people to Allah','Hud trusts in Allah','The dark cloud and the wind','Allah saves Hud and the believers','Good night – the lesson of the story'],
  fr=['Qu’y a-t-il de plus fort que les plus forts ?','Le peuple de ʿAd et la cité d’Iram','L’orgueil au lieu de la gratitude','Le prophète Houd appelle son peuple à Allah','Houd place sa confiance en Allah','Le nuage sombre et le vent','Allah sauve Houd et les croyants','Bonne nuit – la leçon de l’histoire'],
  tr=['En güçlü insanlardan daha güçlü olan ne?','Âd kavmi ve İrem şehri','Şükür yerine kibir','Hûd kavmini Allah’a çağırıyor','Hûd Allah’a tevekkül ediyor','Kara bulut ve rüzgâr','Allah Hûd’u ve müminleri kurtarıyor','İyi geceler – hikâyenin dersi'],
  bs=['Šta je jače od najjačih ljudi?','Narod Ad i grad Irem','Oholost umjesto zahvalnosti','Hud poziva svoj narod Allahu','Hud se oslanja na Allaha','Tamni oblak i vjetar','Allah spašava Huda i vjernike','Laku noć – pouka priče'],
  sq=['Çfarë është më e fortë se njerëzit më të fortë?','Populli i Adit dhe qyteti Irem','Mendjemadhësi në vend të falënderimit','Hudi e thërret popullin te Allahu','Hudi i mbështetet Allahut','Reja e errët dhe era','Allahu e shpëton Hudin dhe besimtarët','Natën e mirë – mësimi i tregimit']),
 dict(n='05', id='vHnXB5RPmik', t=['0:00','0:28','0:55','1:38','2:24','3:03','3:21','3:48','4:12'], q='7:73–79, 11:61–68, 26:141–159, 54:23–31, 89:9, 91:11–15', h=[],
  ar=['ناقة مميزة جدًا','قوم ثمود والبيوت في الصخور','صالح يدعو قومه إلى الله','الآية: ناقة الله','نقض العهد','ثلاثة أيام','الصيحة والرجفة','الله ينجّي صالحًا والمؤمنين','تصبحون على خير – عبرة القصة'],
  en=['A very special camel','The people of Thamud and the houses in the rocks','Prophet Salih calls his people to Allah','The sign: the she-camel of Allah','The promise is broken','Three more days','The mighty blast and the quake','Allah saves Salih and the believers','Good night – the lesson of the story'],
  fr=['Une chamelle très spéciale','Le peuple de Thamoud et les maisons dans les rochers','Le prophète Salih appelle son peuple à Allah','Le signe : la chamelle d’Allah','La promesse est rompue','Encore trois jours','Le cri terrible et le tremblement','Allah sauve Salih et les croyants','Bonne nuit – la leçon de l’histoire'],
  tr=['Çok özel bir deve','Semûd kavmi ve kayalardaki evler','Salih kavmini Allah’a çağırıyor','Mucize: Allah’ın devesi','Söz bozuluyor','Üç gün daha','Korkunç ses ve sarsıntı','Allah Salih’i ve müminleri kurtarıyor','İyi geceler – hikâyenin dersi'],
  bs=['Jedna posebna deva','Narod Semud i kuće u stijenama','Salih poziva svoj narod Allahu','Znak: Allahova deva','Dogovor je prekršen','Još tri dana','Strašan glas i potres','Allah spašava Saliha i vjernike','Laku noć – pouka priče'],
  sq=['Një deve shumë e veçantë','Populli i Themudit dhe shtëpitë në shkëmbinj','Salihu e thërret popullin te Allahu','Shenja: devja e Allahut','Marrëveshja prishet','Edhe tri ditë','Britma e fuqishme dhe dridhja','Allahu e shpëton Salihun dhe besimtarët','Natën e mirë – mësimi i tregimit']),
 dict(n='06', id='4hf0E6VsOk4', t=['0:00','0:44','1:58','3:26','5:04','6:22','6:50'], q='6:74–83, 19:41–48, 21:51–71, 37:88–98, 4:125, 29:26', h=['Sahih al-Bukhari 4563–4564'],
  ar=['نار لا تحرق؟','مدينة الأصنام','الكوكب والقمر والشمس','خطة إبراهيم الشجاعة','النار العظيمة','خليل الله','العبرة وتصبحون على خير'],
  en=['A fire that does not burn?','The city of statues','Star, moon and sun','Abraham’s brave plan','The great fire','The friend of Allah','The lesson & good night'],
  fr=['Un feu qui ne brûle pas ?','La ville des statues','L’étoile, la lune et le soleil','Le plan courageux d’Abraham','Le grand feu','L’ami intime d’Allah','La leçon & bonne nuit'],
  tr=['Yakmayan bir ateş mi?','Heykeller şehri','Yıldız, ay ve güneş','İbrahim’in cesur planı','Büyük ateş','Allah’ın dostu','Ders ve iyi geceler'],
  bs=['Vatra koja ne peče?','Grad kipova','Zvijezda, mjesec i sunce','Ibrahimov hrabri plan','Velika vatra','Allahov prijatelj','Pouka i laku noć'],
  sq=['Një zjarr që nuk djeg?','Qyteti i statujave','Ylli, hëna dhe dielli','Plani i guximshëm i Ibrahimit','Zjarri i madh','Miku i Allahut','Mësimi dhe natën e mirë']),
 dict(n='07', id='O2CZZcXuBa0', t=['0:00','0:47','1:38','3:00','4:07','5:14','5:34'], q='11:69–83, 15:51–77, 26:160–175, 27:54–58, 29:26–35, 51:24–37, 66:10', h=[],
  ar=['الضيوف الغامضون','مهمة لوط','الضيوف عند إبراهيم','الضيوف عند لوط','الليل والصباح','لوط الوفيّ','العبرة وتصبحون على خير'],
  en=['The mysterious guests','Lot’s mission','The guests at Abraham’s house','The guests at Lot’s house','The night and the morning','Faithful Lot','The lesson & good night'],
  fr=['Les invités mystérieux','La mission de Loth','Les invités chez Abraham','Les invités chez Loth','La nuit et le matin','Loth le fidèle','La leçon & bonne nuit'],
  tr=['Gizemli misafirler','Lût’un görevi','İbrahim’in misafirleri','Lût’un misafirleri','Gece ve sabah','Sadık Lût','Ders ve iyi geceler'],
  bs=['Tajanstveni gosti','Lutova misija','Gosti kod Ibrahima','Gosti kod Luta','Noć i jutro','Vjerni Lut','Pouka i laku noć'],
  sq=['Mysafirët misteriozë','Detyra e Lutit','Mysafirët te Ibrahimi','Mysafirët te Luti','Nata dhe mëngjesi','Luti besnik','Mësimi dhe natën e mirë']),
 dict(n='08', id='DfSvCAeJrPI', t=['0:00','0:41','1:55','2:55','3:52','4:34','5:24'], q='14:35–41, 2:125–129, 19:54–55, 22:26', h=['Sahih al-Bukhari 3364–3365'],
  ar=['النبع في الصحراء','الوادي الخالي','سبع مرات بين الصفا والمروة','زمزم','وادٍ مليء بالحياة','الكعبة','العبرة وتصبحون على خير'],
  en=['The spring in the desert','The empty valley','Seven times between Safa and Marwa','Zamzam','A valley full of life','The Kaaba','The lesson & good night'],
  fr=['La source dans le désert','La vallée déserte','Sept fois entre Safa et Marwa','Zamzam','Une vallée pleine de vie','La Kaaba','La leçon & bonne nuit'],
  tr=['Çöldeki kaynak','Boş vadi','Safa ile Merve arasında yedi kez','Zemzem','Hayat dolu bir vadi','Kâbe','Ders ve iyi geceler'],
  bs=['Izvor u pustinji','Prazna dolina','Sedam puta između Safe i Merve','Zemzem','Dolina puna života','Kaba','Pouka i laku noć'],
  sq=['Burimi në shkretëtirë','Lugina e zbrazët','Shtatë herë mes Safës dhe Mervës','Zemzemi','Një luginë plot jetë','Qabja','Mësimi dhe natën e mirë']),
 dict(n='09', id='WPsbvEsJ4S8', t=['0:00','0:48','1:40','3:00','4:27','5:22','7:07'], q='11:69–73, 15:51–56, 51:24–30, 14:39, 37:112–113, 38:45–47, 21:72–73, 19:49, 36:82', h=['Sahih al-Bukhari 3382'],
  ar=['بشارة لا تكاد تُصدَّق','الانتظار الطويل','الضيوف المميزون','سارة تتعجب','ولادة إسحاق','سلسلة من الأنبياء','العبرة وتصبحون على خير'],
  en=['News that is hard to believe','The long wait','The special guests','Sarah is amazed','Isaac is born','A chain of prophets','The lesson & good night'],
  fr=['Une nouvelle à peine croyable','La longue attente','Les invités particuliers','Sarah s’étonne','La naissance d’Isaac','Une lignée de prophètes','La leçon & bonne nuit'],
  tr=['İnanılması zor bir müjde','Uzun bekleyiş','Özel misafirler','Sâre hayret ediyor','İshak doğuyor','Peygamberler zinciri','Ders ve iyi geceler'],
  bs=['Vijest kojoj je teško povjerovati','Dugo čekanje','Posebni gosti','Sara se čudi','Rođenje Ishaka','Lanac vjerovjesnika','Pouka i laku noć'],
  sq=['Një lajm që mezi besohet','Pritja e gjatë','Mysafirët e veçantë','Sara mahnitet','Lindja e Is’hakut','Një zinxhir pejgamberësh','Mësimi dhe natën e mirë']),
 dict(n='10', id='bYMbH2JWOmw', t=['0:00','0:46','1:50','3:14','4:23','5:24','6:36'], q='2:132–133, 11:71, 19:49, 21:72–73, 38:45–47, 12:4–6, 12:11–18, 12:84–87, 12:100', h=[],
  ar=['السؤال المهم','عائلة يعقوب','رؤيا يوسف','اليوم الصعب','سنوات طويلة من الأمل','جواب الأبناء','العبرة وتصبحون على خير'],
  en=['The important question','Jacob’s family','Joseph’s dream','The hard day','Many years of hope','The sons’ answer','The lesson & good night'],
  fr=['La question importante','La famille de Jacob','Le rêve de Joseph','Le jour difficile','De longues années d’espoir','La réponse des fils','La leçon & bonne nuit'],
  tr=['Önemli soru','Yakub’un ailesi','Yusuf’un rüyası','Zor gün','Uzun umut yılları','Oğulların cevabı','Ders ve iyi geceler'],
  bs=['Važno pitanje','Jakubova porodica','Jusufov san','Teški dan','Mnogo godina nade','Odgovor sinova','Pouka i laku noć'],
  sq=['Pyetja e rëndësishme','Familja e Jakubit','Ëndrra e Jusufit','Dita e vështirë','Shumë vite shprese','Përgjigjja e bijve','Mësimi dhe natën e mirë']),
 dict(n='11', id='JkDMNOlskhY', t=['0:00','0:44','2:05','3:06','4:08','5:35','6:55','8:16'], q='12:4–101', h=['Sunan Ibn Majah 1853'],
  ar=['الرؤيا','البئر','شاب أمين','في السجن','رؤيا الملك','الإخوة يأتون','الرؤيا تتحقق','العبرة وتصبحون على خير'],
  en=['The dream','The well','An honest young man','In prison','The king’s dream','The brothers come','The dream comes true','The lesson & good night'],
  fr=['Le rêve','Le puits','Un jeune homme honnête','En prison','Le rêve du roi','Les frères arrivent','Le rêve se réalise','La leçon & bonne nuit'],
  tr=['Rüya','Kuyu','Dürüst bir genç','Zindanda','Kralın rüyası','Kardeşler geliyor','Rüya gerçek oluyor','Ders ve iyi geceler'],
  bs=['San','Bunar','Pošten mladić','U zatvoru','Kraljev san','Braća dolaze','San se ostvaruje','Pouka i laku noć'],
  sq=['Ëndrra','Pusi','Një i ri i ndershëm','Në burg','Ëndrra e mbretit','Vëllezërit vijnë','Ëndrra bëhet realitet','Mësimi dhe natën e mirë']),
 dict(n='12', id='x40FMezIaRA', t=['0:00','0:42','1:52','3:18','4:00','4:50','5:38'], q='21:83–84, 38:41–44', h=['Sahih al-Bukhari 279, 5641','Sahih Muslim 2569','Sunan at-Tirmidhi 2396, 2398','Sahih Ibn Hibban 2898'],
  ar=['مريض في السرير','الابتلاء العظيم','عودوا المريض','دعاء جميل','النبع','جراد من ذهب','العبرة وتصبحون على خير'],
  en=['Sick in bed','The great test','Visit the sick','A beautiful prayer','The spring','Golden locusts','The lesson & good night'],
  fr=['Malade au lit','La grande épreuve','Rendez visite aux malades','Une très belle invocation','La source','Des sauterelles en or','La leçon & bonne nuit'],
  tr=['Yatakta hasta','Büyük imtihan','Hastaları ziyaret edin','Çok güzel bir dua','Kaynak','Altın çekirgeler','Ders ve iyi geceler'],
  bs=['Bolestan u krevetu','Veliko iskušenje','Posjećujte bolesne','Prelijepa dova','Izvor','Zlatni skakavci','Pouka i laku noć'],
  sq=['I sëmurë në shtrat','Sprova e madhe','Vizitoni të sëmurët','Një lutje shumë e bukur','Burimi','Karkalecat e arta','Mësimi dhe natën e mirë']),
 dict(n='13', id='_vrFYGpWaQE', t=['0:00','0:38','1:25','2:16','2:58','3:52','5:18'], q='7:85–93, 11:84–95, 29:45, 83:1–3', h=['Sahih Muslim 102'],
  ar=['هل هذا عدل؟','تجّار مدين','رسالة شعيب','السخرية','التهديد والنجاة','الصدق','العبرة وتصبحون على خير'],
  en=['Is that fair?','The traders of Madyan','Shuaib’s message','The mocking','The threat and the rescue','Being honest','The lesson & good night'],
  fr=['Est-ce juste ?','Les marchands de Madyan','Le message de Chouaïb','Les moqueries','La menace et le sauvetage','Être honnête','La leçon & bonne nuit'],
  tr=['Bu adil mi?','Medyen tüccarları','Şuayb’ın mesajı','Alay','Tehdit ve kurtuluş','Dürüst olmak','Ders ve iyi geceler'],
  bs=['Je li to pravedno?','Trgovci iz Medjena','Šuajbova poruka','Ruganje','Prijetnja i spas','Biti iskren','Pouka i laku noć'],
  sq=['A është e drejtë kjo?','Tregtarët e Medjenit','Mesazhi i Shuajbit','Talljet','Kërcënimi dhe shpëtimi','Të jesh i ndershëm','Mësimi dhe natën e mirë']),
 dict(n='14', id='RPdXVMieWro', t=['0:00','0:40','2:54','3:59','6:08','7:07','8:58'], q='28:4–29, 20:9–77, 26:52–66, 4:164', h=['Sahih al-Bukhari 2004'],
  ar=['رضيع في النهر؟','الصندوق في النهر','في مدين','النار عند الجبل','عند فرعون','البحر','العبرة وتصبحون على خير'],
  en=['A baby in the river?','The basket on the river','In Madyan','The fire on the mountain','Before Pharaoh','The sea','The lesson & good night'],
  fr=['Un bébé dans le fleuve ?','Le coffre sur le fleuve','À Madyan','Le feu sur la montagne','Chez Pharaon','La mer','La leçon & bonne nuit'],
  tr=['Nehirde bir bebek mi?','Nehirdeki sandık','Medyen’de','Dağdaki ateş','Firavun’un huzurunda','Deniz','Ders ve iyi geceler'],
  bs=['Beba u rijeci?','Kovčeg na rijeci','U Medjenu','Vatra na brdu','Kod faraona','More','Pouka i laku noć'],
  sq=['Një foshnjë në lumë?','Arka në lumë','Në Medjen','Zjarri në mal','Te faraoni','Deti','Mësimi dhe natën e mirë']),
 dict(n='15', id='BNDReswMh1s', t=['0:00','0:40','1:43','2:43','3:53','4:59','5:43'], q='19:53, 20:24–47, 20:85–94, 28:34–35, 7:142, 7:150–151, 37:114–122', h=['Sahih al-Bukhari 4416'],
  ar=['أخوان','أمنية موسى','معًا إلى فرعون','هارون يثبت في مكانه','اللقاء من جديد','مكانة عظيمة','العبرة وتصبحون على خير'],
  en=['Two brothers','Moses’ wish','Together to Pharaoh','Aaron holds his ground','Meeting again','A place of honour','The lesson & good night'],
  fr=['Deux frères','Le souhait de Moïse','Ensemble chez Pharaon','Aaron tient bon','Les retrouvailles','Une place d’honneur','La leçon & bonne nuit'],
  tr=['İki kardeş','Musa’nın dileği','Birlikte Firavun’a','Harun yerinde duruyor','Yeniden kavuşma','Şerefli bir makam','Ders ve iyi geceler'],
  bs=['Dva brata','Musaova želja','Zajedno kod faraona','Harun ostaje čvrst','Ponovni susret','Počasno mjesto','Pouka i laku noć'],
  sq=['Dy vëllezër','Dëshira e Musait','Së bashku te faraoni','Haruni qëndron i palëkundur','Takimi përsëri','Një vend nderi','Mësimi dhe natën e mirë']),
 dict(n='16', id='mfIgtD9hTl8', t=['0:00','0:36','1:37','2:34','3:19','4:03'], q='21:85–86, 38:48, 2:153, 39:10', h=['Sahih al-Bukhari 1469','Sahih Muslim 1053'],
  ar=['اسم غامض','ماذا يقول القرآن','ما هو الصبر؟','أن تكون من الصالحين','ما لا نعرفه','العبرة وتصبحون على خير'],
  en=['A mysterious name','What the Quran says','What is patience?','Being righteous','What we do not know','The lesson & good night'],
  fr=['Un nom mystérieux','Ce que dit le Coran','Qu’est-ce que la patience ?','Être vertueux','Ce que nous ne savons pas','La leçon & bonne nuit'],
  tr=['Gizemli bir isim','Kur’an ne diyor','Sabır nedir?','Salih olmak','Bilmediklerimiz','Ders ve iyi geceler'],
  bs=['Tajanstveno ime','Šta kaže Kur’an','Šta je sabur?','Biti dobar','Ono što ne znamo','Pouka i laku noć'],
  sq=['Një emër misterioz','Çfarë thotë Kurani','Çfarë është durimi?','Të jesh i mirë','Çfarë nuk dimë','Mësimi dhe natën e mirë']),
]

def block(ep, L):
    lines = [HDR[L]] + [f"{t} {c}" for t, c in zip(ep['t'], ep[L])]
    if L == 'ar':
        had = [HAD_AR[next(k for k in HAD_AR if h.startswith(k))] + h[len(next(k for k in HAD_AR if h.startswith(k))):] for h in ep['h']]
    else:
        had = ep['h']
    src = f"{SRC[L]} {ep['q']}" + (' · ' + ', '.join(had) if had else '') + '.'
    return '\n'.join(lines) + '\n\n' + src

out = {}
for ep in EP:
    for L in ['ar','en','fr','tr','bs','sq']:
        assert len(ep[L]) == len(ep['t']), (ep['n'], L)
    out[ep['id']] = {L: block(ep, L) for L in ['ar','en','fr','tr','bs','sq']}
json.dump(out, open('/home/claude/boa-render/out/desc_i18n_blocks.json','w'), ensure_ascii=False, indent=1)
print(out['mCiK-z7qkb8']['ar']); print(out['x40FMezIaRA']['en'])
