--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4
-- Dumped by pg_dump version 16.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: food_allergen_classification; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '無糖冰綠茶(小)', '{冰綠茶(無糖),冰綠茶(無糖)}', false, '{}', 0, 25.018175, 121.53333, '2026-05-03 00:49:30.459896');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '大蛋捲冰淇淋', '{甜筒酥杯,聖代奶漿,甜筒酥杯,聖代奶漿}', true, '{乳製品}', 1, 25.018175, 121.53333, '2026-05-03 00:49:30.4621');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '薯餅', '{葵花油,薯餅}', false, '{}', 0, 25.018175, 121.53333, '2026-05-03 00:49:30.462125');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '無糖冰紅茶(中)', '{冰紅茶(無糖),冰紅茶(無糖)}', false, '{}', 0, 25.018175, 121.53333, '2026-05-03 00:49:30.462134');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '義式濃縮咖啡', '{100%阿拉比卡咖啡豆,100%阿拉比卡咖啡豆}', false, '{}', 0, 25.018175, 121.53333, '2026-05-03 00:49:30.462143');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '冰紅茶(檸檬風味) (小)', '{飛想茶檸檬口味紅茶,飛想茶檸檬口味紅茶}', false, '{}', 0, 25.018175, 121.53333, '2026-05-03 00:49:30.462151');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '蘋果綜合果汁', '{果汁時刻100%蘋果綜合果汁,果汁時刻100%蘋果綜合果汁}', false, '{}', 0, 25.018175, 121.53333, '2026-05-03 00:49:30.462159');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '蛋捲冰淇淋', '{聖代奶漿,蛋捲杯,聖代奶漿,蛋捲杯}', true, '{乳製品}', 1, 25.018175, 121.53333, '2026-05-03 00:49:30.462175');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '無糖冰紅茶(小)', '{冰紅茶(無糖),冰紅茶(無糖)}', false, '{}', 0, 25.018175, 121.53333, '2026-05-03 00:49:30.462183');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '麥克鷄塊(4塊)', '{麥克雞塊,葵花油}', true, '{麩質穀物}', 1, 25.018175, 121.53333, '2026-05-03 00:49:30.46219');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '玉米湯(大)', '{玉米湯粉,玉米粒}', false, '{}', 0, 25.018175, 121.53333, '2026-05-03 00:49:30.462196');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '吉事蛋堡', '{吉事(乾酪),香蒜風味醬,洗選蛋,漢堡麵包,番茄醬}', true, '{乳製品,麩質穀物}', 2, 25.018175, 121.53333, '2026-05-03 00:49:30.462206');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '可口可樂(小)', '{可口可樂汽水,可口可樂汽水}', false, '{}', 0, 25.018175, 121.53333, '2026-05-03 00:49:30.462214');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '青蔬滿福堡', '{洋火腿,切片生菜,吉事(乾酪),滿福麵包,洗選蛋}', true, '{乳製品,麩質穀物}', 2, 25.018175, 121.53333, '2026-05-03 00:49:30.46222');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '可口可樂(中)', '{可口可樂汽水,可口可樂汽水}', false, '{}', 0, 25.018175, 121.53333, '2026-05-03 00:49:30.462227');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '麥克鷄塊(10塊)', '{麥克雞塊,葵花油}', false, '{}', 0, 25.018175, 121.53333, '2026-05-03 00:49:33.228536');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '雙倍OREO冰炫風', '{聖代奶漿,奧利奧餅乾碎片}', true, '{乳製品}', 1, 25.018175, 121.53333, '2026-05-03 00:49:33.228604');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '豬肉蛋堡', '{切片生菜,吉事(乾酪),香蒜風味醬,鮮肉餅,洗選蛋,漢堡麵包,番茄醬}', true, '{乳製品,麩質穀物}', 2, 25.018175, 121.53333, '2026-05-03 00:49:33.228612');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '可口可樂zero(中)', '{可口可樂ZERO汽水,可口可樂ZERO汽水}', false, '{}', 0, 25.018175, 121.53333, '2026-05-03 00:49:33.228619');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '蜂蜜紅茶(冰)', '{冰紅茶(無糖),冰塊,龍眼荔枝蜜,冰紅茶(無糖),冰塊,龍眼荔枝蜜}', false, '{}', 0, 25.018175, 121.53333, '2026-05-03 00:49:33.228626');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '熱奶茶', '{牛乳,熱紅茶,牛乳,熱紅茶}', true, '{乳製品}', 1, 25.018175, 121.53333, '2026-05-03 00:49:33.228631');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '可口可樂zero(小)', '{可口可樂ZERO汽水,可口可樂ZERO汽水}', false, '{}', 0, 25.018175, 121.53333, '2026-05-03 00:49:33.228637');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '蜂蜜奶茶(冰)', '{冰紅茶(無糖),冰塊,龍眼荔枝蜜,厚牛乳,冰紅茶(無糖),冰塊,龍眼荔枝蜜,厚牛乳}', true, '{乳製品}', 1, 25.018175, 121.53333, '2026-05-03 00:49:33.228642');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '豬肉滿福堡加蛋', '{吉事(乾酪),滿福麵包,鮮肉餅,洗選蛋}', true, '{乳製品,麩質穀物}', 2, 25.018175, 121.53333, '2026-05-03 00:49:33.228648');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '冰紅茶(檸檬風味) (中)', '{飛想茶檸檬口味紅茶,飛想茶檸檬口味紅茶}', false, '{}', 0, 25.018175, 121.53333, '2026-05-03 00:49:33.228654');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '熱經典那堤', '{牛乳,100%阿拉比卡咖啡豆,牛乳,100%阿拉比卡咖啡豆}', true, '{乳製品}', 1, 25.018175, 121.53333, '2026-05-03 00:49:33.228661');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '蘋果派', '{葵花油,蘋果派}', false, '{}', 0, 25.018175, 121.53333, '2026-05-03 00:49:33.228667');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', 'Evian天然礦泉水', '{Evian天然礦泉水,Evian天然礦泉水}', false, '{}', 0, 25.018175, 121.53333, '2026-05-03 00:49:33.228671');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '鬆餅 (3片)', '{冷凍鬆餅}', true, '{麩質穀物}', 1, 25.018175, 121.53333, '2026-05-03 00:49:33.228678');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '和德昌股份有限公司', '麥當勞', '現烤焙果', '{焙果麵包,乳酪抹醬}', true, '{乳製品,麩質穀物}', 2, 25.018175, 121.53333, '2026-05-03 00:49:33.228683');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '薯餅', '{薯餅,油炸油(加盟店各自採購)}', false, '{}', 0, 25.028894, 121.52579, '2026-05-03 00:49:36.367828');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '薯條', '{薯條,油炸油(加盟店各自採購)}', false, '{}', 0, 25.028894, 121.52579, '2026-05-03 00:49:36.367891');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '蘿蔔糕', '{蘿蔔糕}', false, '{}', 0, 25.028894, 121.52579, '2026-05-03 00:49:36.367896');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '巧克力厚片', '{巧克力抹醬,厚片吐司(加盟店各自採購)}', true, '{乳製品,麩質穀物}', 2, 25.028894, 121.52579, '2026-05-03 00:49:36.367901');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '花生厚片', '{花生抹醬,厚片吐司(加盟店各自採購)}', true, '{花生,麩質穀物}', 2, 25.028894, 121.52579, '2026-05-03 00:49:36.367905');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '椰香奶酥厚片', '{椰香奶酥抹醬,厚片吐司(加盟店各自採購)}', true, '{乳製品,麩質穀物}', 2, 25.028894, 121.52579, '2026-05-03 00:49:36.367909');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '法式田園鮪魚', '{美生菜(加盟店各自採購),鮪魚,小沙拉醬,起司片,法式麵包}', true, '{海鮮類,乳製品,麩質穀物}', 3, 25.028894, 121.52579, '2026-05-03 00:49:36.367914');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '培根蛋堡', '{美生菜(加盟店各自採購),蕃茄(加盟店各自採購),培根,雞蛋(加盟店各自採購),漢堡(加盟店各自採購)}', true, '{麩質穀物}', 1, 25.028894, 121.52579, '2026-05-03 00:49:36.367918');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '豬排蛋堡', '{美生菜(加盟店各自採購),雞蛋(加盟店各自採購),漢堡(加盟店各自採購),黑胡椒豬排}', true, '{麩質穀物}', 1, 25.028894, 121.52579, '2026-05-03 00:49:36.367921');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '卡啦雞腿蛋堡', '{美生菜(加盟店各自採購),小沙拉醬,卡啦雞腿,漢堡(加盟店各自採購)}', true, '{麩質穀物}', 1, 25.028894, 121.52579, '2026-05-03 00:49:36.367926');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '豬排蛋餅', '{蛋餅皮,小沙拉醬,雞蛋(加盟店各自採購),黑胡椒豬排}', true, '{}', 0, 25.028894, 121.52579, '2026-05-03 00:49:36.367929');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '火腿蛋餅', '{蛋餅皮,雞蛋(加盟店各自採購),火腿}', true, '{}', 0, 25.028894, 121.52579, '2026-05-03 00:49:36.367934');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '玉米蛋餅', '{玉米粒,蛋餅皮,雞蛋(加盟店各自採購)}', false, '{}', 0, 25.028894, 121.52579, '2026-05-03 00:49:36.367938');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '豬排蛋吐司', '{美生菜(加盟店各自採購),小黃瓜(加盟店各自採購),雞蛋(加盟店各自採購),吐司(加盟店各自採購),黑胡椒豬排}', true, '{麩質穀物}', 1, 25.028894, 121.52579, '2026-05-03 00:49:36.367943');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '鮪魚蛋吐司', '{美生菜(加盟店各自採購),鮪魚,小沙拉醬,小黃瓜(加盟店各自採購),雞蛋(加盟店各自採購),吐司(加盟店各自採購)}', true, '{海鮮類,麩質穀物}', 2, 25.028894, 121.52579, '2026-05-03 00:49:36.367948');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '招牌總匯三明治', '{蕃茄(加盟店各自採購),小黃瓜(加盟店各自採購),雞蛋(加盟店各自採購),吐司(加盟店各自採購),漢堡肉,火腿}', false, '{}', 0, 25.028894, 121.52579, '2026-05-03 00:49:39.92965');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '培根蛋吐司', '{美生菜(加盟店各自採購),培根,雞蛋(加盟店各自採購),吐司(加盟店各自採購)}', false, '{}', 0, 25.028894, 121.52579, '2026-05-03 00:49:39.929724');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '錫蘭紅茶', '{砂糖(加盟店各自採購),錫蘭紅茶}', false, '{}', 0, 25.028894, 121.52579, '2026-05-03 00:49:39.929735');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '顆粒柳橙汁', '{顆粒柳橙汁}', false, '{}', 0, 25.028894, 121.52579, '2026-05-03 00:49:39.929743');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '優鮮堡實業有限公司', '鮮堡漢堡', '芒果果汁', '{芒果果汁}', false, '{}', 0, 25.028894, 121.52579, '2026-05-03 00:49:39.92975');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '齋聖彥有限公司', '味亦美', '培根蛋三明治', '{吐司,"雞蛋(直營店使用,加盟店各自採購)",培根,沙拉醬,番茄,生菜,洋蔥}', false, '{}', 0, 25.070799, 121.6127, '2026-05-03 00:49:39.92976');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '齋聖彥有限公司', '味亦美', '起司蛋三明治', '{吐司,"雞蛋(直營店使用,加盟店各自採購)",沙拉醬,番茄,生菜,洋蔥,起司}', true, '{乳製品}', 1, 25.070799, 121.6127, '2026-05-03 00:49:39.929768');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '齋聖彥有限公司', '味亦美', '咔啦雞腿三明治', '{吐司,"雞蛋(直營店使用,加盟店各自採購)",沙拉醬,番茄,生菜,洋蔥,咔啦雞腿}', false, '{}', 0, 25.070799, 121.6127, '2026-05-03 00:49:39.929776');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '齋聖彥有限公司', '味亦美', '椰香吐司', '{吐司,椰香醬}', false, '{}', 0, 25.070799, 121.6127, '2026-05-03 00:49:39.929783');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '齋聖彥有限公司', '味亦美', '巧克力吐司', '{吐司,巧克力醬}', false, '{}', 0, 25.070799, 121.6127, '2026-05-03 00:49:39.92979');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '齋聖彥有限公司', '味亦美', '原味蛋餅', '{蛋餅皮,"雞蛋(直營店使用,加盟店各自採購)"}', false, '{}', 0, 25.070799, 121.6127, '2026-05-03 00:49:39.929798');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '齋聖彥有限公司', '味亦美', '起司蛋餅', '{蛋餅皮,"雞蛋(直營店使用,加盟店各自採購)",起司}', true, '{乳製品}', 1, 25.070799, 121.6127, '2026-05-03 00:49:39.929805');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '齋聖彥有限公司', '味亦美', '黑胡椒豬排蛋餅', '{黑胡椒豬排,蛋餅皮,"雞蛋(直營店使用,加盟店各自採購)"}', false, '{}', 0, 25.070799, 121.6127, '2026-05-03 00:49:39.929812');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '齋聖彥有限公司', '味亦美', '無糖豆漿', '{無糖豆漿}', false, '{}', 0, 25.070799, 121.6127, '2026-05-03 00:49:39.92982');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '齋聖彥有限公司', '味亦美', '紅茶', '{紅茶,砂糖}', false, '{}', 0, 25.070799, 121.6127, '2026-05-03 00:49:39.929828');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '齋聖彥有限公司', '味亦美', '綠茶', '{綠茶}', false, '{}', 0, 25.070799, 121.6127, '2026-05-03 00:49:43.656191');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '齋聖彥有限公司', '味亦美', '辣味咔啦雞腿漢堡', '{芝麻漢堡,辣味咔啦雞腿,"雞蛋(直營店使用,加盟店各自採購)",沙拉醬,番茄,生菜,洋蔥}', false, '{}', 0, 25.070799, 121.6127, '2026-05-03 00:49:43.656314');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '齋聖彥有限公司', '味亦美', '黑胡椒豬排漢堡', '{芝麻漢堡,黑胡椒豬排,"雞蛋(直營店使用,加盟店各自採購)",沙拉醬,番茄,生菜,洋蔥}', false, '{}', 0, 25.070799, 121.6127, '2026-05-03 00:49:43.656324');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '齋聖彥有限公司', '味亦美', '起司蛋堡', '{芝麻漢堡,"雞蛋(直營店使用,加盟店各自採購)",沙拉醬,番茄,生菜,洋蔥,起司}', true, '{乳製品}', 1, 25.070799, 121.6127, '2026-05-03 00:49:43.656329');
INSERT INTO public.food_allergen_classification VALUES ('新北市', '屹澧有限公司', '城市漢堡', '湯種巧克力吐司', '{巧克力醬,湯種吐司}', false, '{}', 0, 24.999573, 121.5393, '2026-05-03 00:50:09.480365');
INSERT INTO public.food_allergen_classification VALUES ('新北市', '屹澧有限公司', '城市漢堡', '湯種花生吐司', '{花生醬,湯種吐司}', true, '{花生}', 1, 24.999573, 121.5393, '2026-05-03 00:50:09.480487');
INSERT INTO public.food_allergen_classification VALUES ('新北市', '屹澧有限公司', '城市漢堡', '鮮嫩鱈魚美式堡', '{漢堡,番茄(各分店自理),鱈魚,美生菜(各分店自理),沙拉油,漢堡醬}', true, '{海鮮類}', 1, 24.999573, 121.5393, '2026-05-03 00:50:09.480504');
INSERT INTO public.food_allergen_classification VALUES ('新北市', '屹澧有限公司', '城市漢堡', '醬燒豬排美式堡', '{漢堡,番茄(各分店自理),美生菜(各分店自理),漢堡醬,豬排}', false, '{}', 0, 24.999573, 121.5393, '2026-05-03 00:50:09.480514');
INSERT INTO public.food_allergen_classification VALUES ('新北市', '屹澧有限公司', '城市漢堡', '麥香雞美式堡', '{漢堡,番茄(各分店自理),美生菜(各分店自理),沙拉油,漢堡醬,雞堡}', false, '{}', 0, 24.999573, 121.5393, '2026-05-03 00:50:09.480523');
INSERT INTO public.food_allergen_classification VALUES ('新北市', '屹澧有限公司', '城市漢堡', '起司蛋餅', '{雞蛋(各分店自理),起司片,蛋餅}', true, '{乳製品}', 1, 24.999573, 121.5393, '2026-05-03 00:50:09.480531');
INSERT INTO public.food_allergen_classification VALUES ('新北市', '屹澧有限公司', '城市漢堡', '燒肉蛋餅', '{雞蛋(各分店自理),燒肉,蛋餅}', false, '{}', 0, 24.999573, 121.5393, '2026-05-03 00:50:09.480538');
INSERT INTO public.food_allergen_classification VALUES ('新北市', '屹澧有限公司', '城市漢堡', '燻雞蛋餅', '{雞蛋(各分店自理),燻雞,蛋餅}', false, '{}', 0, 24.999573, 121.5393, '2026-05-03 00:50:09.480546');
INSERT INTO public.food_allergen_classification VALUES ('新北市', '屹澧有限公司', '城市漢堡', '奶茶', '{紅茶茶包,奶茶奶粉}', true, '{乳製品}', 1, 24.999573, 121.5393, '2026-05-03 00:50:09.480553');
INSERT INTO public.food_allergen_classification VALUES ('新北市', '屹澧有限公司', '城市漢堡', '紅茶', '{紅茶茶包}', false, '{}', 0, 24.999573, 121.5393, '2026-05-03 00:50:09.480597');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '呷尚寶興業股份有限公司', '呷尚寶', '香雞三明治', '{小黃瓜,香雞排,美生菜,沙拉醬,沙拉油,吐司}', false, '{}', 0, 25.026867, 121.55661, '2026-05-03 00:50:09.480607');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '呷尚寶興業股份有限公司', '呷尚寶', '卡拉雞三明治', '{小黃瓜,卡啦雞腿排,美生菜,沙拉醬,沙拉油,吐司}', false, '{}', 0, 25.026867, 121.55661, '2026-05-03 00:50:09.480615');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '呷尚寶興業股份有限公司', '呷尚寶', '豬排三明治', '{小黃瓜,豬排,美生菜,沙拉醬,沙拉油,吐司}', false, '{}', 0, 25.026867, 121.55661, '2026-05-03 00:50:09.480622');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '呷尚寶興業股份有限公司', '呷尚寶', '巧克力吐司', '{巧克力醬,吐司}', false, '{}', 0, 25.026867, 121.55661, '2026-05-03 00:50:09.480629');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '呷尚寶興業股份有限公司', '呷尚寶', '奶油吐司', '{奶油醬,吐司}', false, '{}', 0, 25.026867, 121.55661, '2026-05-03 00:50:19.682657');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '呷尚寶興業股份有限公司', '呷尚寶', '椰香吐司', '{椰香醬,吐司}', false, '{}', 0, 25.026867, 121.55661, '2026-05-03 00:50:19.682736');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '呷尚寶興業股份有限公司', '呷尚寶', '原味蛋餅', '{雞蛋,蛋餅皮,沙拉油}', false, '{}', 0, 25.026867, 121.55661, '2026-05-03 00:50:19.682748');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '呷尚寶興業股份有限公司', '呷尚寶', '火腿蛋餅', '{雞蛋,蛋餅皮,火腿,沙拉油}', false, '{}', 0, 25.026867, 121.55661, '2026-05-03 00:50:19.682756');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '呷尚寶興業股份有限公司', '呷尚寶', '豬排蛋餅', '{豬排,雞蛋,蛋餅皮,沙拉油}', false, '{}', 0, 25.026867, 121.55661, '2026-05-03 00:50:19.682763');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '呷尚寶興業股份有限公司', '呷尚寶', '豬肉陽光堡', '{陽光堡,豬肉漢堡排,番茄,美生菜,洋蔥,沙拉醬,沙拉油}', false, '{}', 0, 25.026867, 121.55661, '2026-05-03 00:50:19.682771');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '呷尚寶興業股份有限公司', '呷尚寶', '豬排陽光堡', '{陽光堡,豬排,番茄,美生菜,洋蔥,沙拉醬,沙拉油}', false, '{}', 0, 25.026867, 121.55661, '2026-05-03 00:50:19.682779');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '呷尚寶興業股份有限公司', '呷尚寶', '香雞陽光堡', '{陽光堡,番茄,美生菜,洋蔥,沙拉醬,沙拉油,香雞堡}', false, '{}', 0, 25.026867, 121.55661, '2026-05-03 00:50:19.682787');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '呷尚寶興業股份有限公司', '呷尚寶', '紅茶', '{砂糖,紅茶茶包}', false, '{}', 0, 25.026867, 121.55661, '2026-05-03 00:50:19.682794');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '呷尚寶興業股份有限公司', '呷尚寶', '奶茶', '{砂糖,紅茶茶包,奶精}', true, '{乳製品}', 1, 25.026867, 121.55661, '2026-05-03 00:50:19.682801');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '呷尚寶興業股份有限公司', '呷尚寶', '咖啡', '{砂糖,咖啡粉}', false, '{}', 0, 25.026867, 121.55661, '2026-05-03 00:50:19.682809');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '金斗雲企業有限公司', '漢堡大師', '煎蛋土司', '{萵苣,番茄,沙拉,洗選雞蛋,洗選雞蛋,吐司,吐司}', false, '{}', 0, 25.037794, 121.574646, '2026-05-03 00:50:19.682818');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '金斗雲企業有限公司', '漢堡大師', '培根蛋吐司', '{培根(加拿大),萵苣,番茄,沙拉,洗選雞蛋,洗選雞蛋,洗選雞蛋,吐司,吐司}', false, '{}', 0, 25.037794, 121.574646, '2026-05-03 00:50:19.682827');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '金斗雲企業有限公司', '漢堡大師', '起司蛋吐司', '{起司片,萵苣,番茄,沙拉,洗選雞蛋,洗選雞蛋,洗選雞蛋,吐司,吐司}', true, '{乳製品}', 1, 25.037794, 121.574646, '2026-05-03 00:50:19.682833');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '金斗雲企業有限公司', '漢堡大師', '花生吐司', '{花生抹醬,吐司,吐司}', true, '{花生}', 1, 25.037794, 121.574646, '2026-05-03 00:50:19.68284');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '金斗雲企業有限公司', '漢堡大師', '椰香吐司', '{椰香醬,吐司,吐司}', false, '{}', 0, 25.037794, 121.574646, '2026-05-03 00:50:28.846657');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '金斗雲企業有限公司', '漢堡大師', '巧克力吐司', '{福汎巧克力醬,吐司,吐司}', false, '{}', 0, 25.037794, 121.574646, '2026-05-03 00:50:28.847466');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '金斗雲企業有限公司', '漢堡大師', '起司蛋餅', '{起司片,蔥花蛋餅皮,酥脆蛋餅皮,洗選雞蛋,洗選雞蛋,洗選雞蛋}', true, '{乳製品}', 1, 25.037794, 121.574646, '2026-05-03 00:50:28.847476');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '金斗雲企業有限公司', '漢堡大師', '原味蛋餅', '{蔥花蛋餅皮,酥脆蛋餅皮,洗選雞蛋,洗選雞蛋,洗選雞蛋}', false, '{}', 0, 25.037794, 121.574646, '2026-05-03 00:50:28.847483');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '金斗雲企業有限公司', '漢堡大師', '培根蛋餅', '{培根(加拿大),蔥花蛋餅皮,酥脆蛋餅皮,洗選雞蛋,洗選雞蛋,洗選雞蛋}', false, '{}', 0, 25.037794, 121.574646, '2026-05-03 00:50:28.847489');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '金斗雲企業有限公司', '漢堡大師', '紅茶', '{紅茶茶包}', false, '{}', 0, 25.037794, 121.574646, '2026-05-03 00:50:28.847496');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '金斗雲企業有限公司', '漢堡大師', '豆漿', '{豆漿}', true, '{蠶豆}', 1, 25.037794, 121.574646, '2026-05-03 00:50:28.847503');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '金斗雲企業有限公司', '漢堡大師', '奶茶', '{紅茶茶包,奶精水}', true, '{乳製品}', 1, 25.037794, 121.574646, '2026-05-03 00:50:28.847509');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '金斗雲企業有限公司', '漢堡大師', '香雞堡', '{起司片,香雞肉,萵苣,番茄,沙拉,洗選雞蛋,洗選雞蛋,漢堡皮,漢堡皮}', true, '{乳製品,麩質穀物}', 2, 25.037794, 121.574646, '2026-05-03 00:50:28.847514');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '金斗雲企業有限公司', '漢堡大師', '起司蛋漢堡', '{起司片,萵苣,番茄,沙拉,洗選雞蛋,洗選雞蛋,洗選雞蛋,漢堡皮,漢堡皮}', true, '{乳製品,麩質穀物}', 2, 25.037794, 121.574646, '2026-05-03 00:50:28.847521');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '金斗雲企業有限公司', '漢堡大師', '培根漢堡', '{培根(加拿大),萵苣,番茄,沙拉,洗選雞蛋,洗選雞蛋,漢堡皮,漢堡皮}', false, '{}', 0, 25.037794, 121.574646, '2026-05-03 00:50:28.847528');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '輝久股份有限公司', '麥町吐司工房', '中秋烤肉蛋吐司', '{沙拉油,沙拉醬,豬排,雞蛋,吐司}', false, '{}', 0, 25.046352, 121.50755, '2026-05-03 00:50:29.515678');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '輝久股份有限公司', '麥町吐司工房', '和風鮪魚蛋吐司', '{美生菜,沙拉油,沙拉醬,雞蛋,鮪魚,吐司}', true, '{海鮮類}', 1, 25.046352, 121.50755, '2026-05-03 00:50:29.515745');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '輝久股份有限公司', '麥町吐司工房', '培根吐司', '{培根,美生菜,沙拉油,沙拉醬,雞蛋,吐司}', false, '{}', 0, 25.046352, 121.50755, '2026-05-03 00:50:29.515751');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '輝久股份有限公司', '麥町吐司工房', '美人蛋餅', '{蛋餅皮,蔥,沙拉油,雞蛋}', false, '{}', 0, 25.046352, 121.50755, '2026-05-03 00:50:31.249216');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '輝久股份有限公司', '麥町吐司工房', '和風鮪魚蔥花蛋餅', '{蛋餅皮,蔥,沙拉油,雞蛋,鮪魚}', true, '{海鮮類}', 1, 25.046352, 121.50755, '2026-05-03 00:50:31.249277');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '輝久股份有限公司', '麥町吐司工房', '黃金玉米蔥花蛋餅', '{蛋餅皮,蔥,玉米粒,沙拉油,雞蛋}', false, '{}', 0, 25.046352, 121.50755, '2026-05-03 00:50:31.249323');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '輝久股份有限公司', '麥町吐司工房', '國王厚牛', '{漢堡麵包,厚牛,美生菜,沙拉油,沙拉醬}', false, '{}', 0, 25.046352, 121.50755, '2026-05-03 00:50:31.249327');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '輝久股份有限公司', '麥町吐司工房', '中秋烤肉漢堡', '{漢堡麵包,美生菜,沙拉油,沙拉醬,豬排,雞蛋}', false, '{}', 0, 25.046352, 121.50755, '2026-05-03 00:50:31.24933');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '輝久股份有限公司', '麥町吐司工房', '和風鮪魚蛋漢堡', '{漢堡麵包,美生菜,沙拉油,沙拉醬,雞蛋,鮪魚}', true, '{海鮮類}', 1, 25.046352, 121.50755, '2026-05-03 00:50:31.249334');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '蘋果貳零参(有)公司', 'APPLE 203', '里肌豬排蛋吐司', '{沙拉醬,吐司,203豬排,沙拉油,雞蛋,美生菜}', false, '{}', 0, 25.034298, 121.507385, '2026-05-03 00:50:31.24934');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '蘋果貳零参(有)公司', 'APPLE 203', '香煎培根蛋吐司', '{沙拉醬,吐司,沙拉油,雞蛋,培根,美生菜}', false, '{}', 0, 25.034298, 121.507385, '2026-05-03 00:50:31.249343');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '蘋果貳零参(有)公司', 'APPLE 203', '和風鮪魚蛋吐司', '{沙拉醬,吐司,沙拉油,雞蛋,美生菜,鮪魚}', true, '{海鮮類}', 1, 25.034298, 121.507385, '2026-05-03 00:50:31.249371');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '蘋果貳零参(有)公司', 'APPLE 203', '原味蛋餅', '{沙拉油,雞蛋,蛋餅皮}', false, '{}', 0, 25.034298, 121.507385, '2026-05-03 00:50:31.249375');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '蘋果貳零参(有)公司', 'APPLE 203', '黃金玉米蛋餅', '{玉米,沙拉油,雞蛋,蛋餅皮}', false, '{}', 0, 25.034298, 121.507385, '2026-05-03 00:50:31.249379');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '蘋果貳零参(有)公司', 'APPLE 203', '香煎培根蛋餅', '{沙拉油,雞蛋,培根,蛋餅皮}', false, '{}', 0, 25.034298, 121.507385, '2026-05-03 00:50:31.249383');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '蘋果貳零参(有)公司', 'APPLE 203', '里肌豬排蛋漢堡', '{沙拉醬,203豬排,沙拉油,雞蛋,漢堡,美生菜,蕃茄}', false, '{}', 0, 25.034298, 121.507385, '2026-05-03 00:50:31.249386');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '蘋果貳零参(有)公司', 'APPLE 203', '香煎培根蛋漢堡', '{沙拉醬,沙拉油,雞蛋,漢堡,培根,美生菜,蕃茄}', false, '{}', 0, 25.034298, 121.507385, '2026-05-03 00:50:31.24939');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '蘋果貳零参(有)公司', 'APPLE 203', '和風鮪魚蛋漢堡', '{沙拉醬,沙拉油,雞蛋,漢堡,美生菜,蕃茄,鮪魚}', true, '{海鮮類}', 1, 25.034298, 121.507385, '2026-05-03 00:50:31.249393');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '揚秦國際企業股份有限公司', '炸雞大獅', '無骨嫩雞胸蓋飯', '{去皮腿絞肉,米,油,胸排,黃瓜,花椰菜,玉米筍}', false, '{}', 0, 25.015795, 121.532295, '2026-05-03 00:50:43.702959');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '揚秦國際企業股份有限公司', '炸雞大獅', '半雞餐8塊餐', '{半雞,油}', false, '{}', 0, 25.015795, 121.532295, '2026-05-03 00:50:43.703038');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '揚秦國際企業股份有限公司', '炸雞大獅', '臻寶去骨腿丁蓋飯', '{米,油,黃瓜,蒜香辣椒醬,花椰菜,腿丁,腿丁,腿丁,腿丁,玉米筍,去皮腿絞肉,去皮腿絞肉,紅辣椒}', false, '{}', 0, 25.015795, 121.532295, '2026-05-03 00:50:43.703049');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '揚秦國際企業股份有限公司', '炸雞大獅', '酥炸蝦片', '{油,蝦餅}', true, '{海鮮類}', 1, 25.015795, 121.532295, '2026-05-03 00:50:43.703061');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '揚秦國際企業股份有限公司', '炸雞大獅', '去骨腿排蓋飯', '{米,油,黃瓜,蒜香辣椒醬,花椰菜,玉米筍,去皮腿絞肉,去皮腿絞肉,腿丁,腿丁,腿丁,腿丁}', false, '{}', 0, 25.015795, 121.532295, '2026-05-03 00:50:43.70307');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '揚秦國際企業股份有限公司', '炸雞大獅', '大獅雞排飯', '{去皮腿絞肉,玉米筍,米,胸排,油,黃瓜,花椰菜}', false, '{}', 0, 25.015795, 121.532295, '2026-05-03 00:50:43.703087');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '揚秦國際企業股份有限公司', '炸雞大獅', '雞翅', '{油,腿丁}', false, '{}', 0, 25.015795, 121.532295, '2026-05-03 00:50:49.787456');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '揚秦國際企業股份有限公司', '炸雞大獅', '嫩雞蓋飯', '{米,油,胸排,黃瓜,蒜香辣椒醬,花椰菜,玉米筍}', false, '{}', 0, 25.015795, 121.532295, '2026-05-03 00:50:49.787531');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '揚秦國際企業股份有限公司', '炸雞大獅', '台式椒鹽臻寶腿丁蓋飯', '{三色豆,米,黃瓜,腿丁,蒜香辣椒醬,玉米筍,調味胡椒鹽}', false, '{}', 0, 25.015795, 121.532295, '2026-05-03 00:50:49.787543');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '揚秦國際企業股份有限公司', '炸雞大獅', '大獅紅茶', '{紅茶,紅茶,糖}', false, '{}', 0, 25.015795, 121.532295, '2026-05-03 00:50:49.787551');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '揚秦國際企業股份有限公司', '炸雞大獅', '花枝丸', '{油,花枝丸}', true, '{海鮮類}', 1, 25.015795, 121.532295, '2026-05-03 00:50:49.787563');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '揚秦國際企業股份有限公司', '炸雞大獅', '無骨嫩雞胸', '{油,胸排}', false, '{}', 0, 25.015795, 121.532295, '2026-05-03 00:50:49.787571');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '揚秦國際企業股份有限公司', '炸雞大獅', '獅奶殺手', '{奶精,紅茶,紅茶,糖}', true, '{乳製品}', 1, 25.015795, 121.532295, '2026-05-03 00:50:49.787578');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '揚秦國際企業股份有限公司', '炸雞大獅', '黃金雞軟骨', '{油,雞軟骨}', false, '{}', 0, 25.015795, 121.532295, '2026-05-03 00:50:49.787586');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '揚秦國際企業股份有限公司', '炸雞大獅', '青春四季豆', '{四季豆,油,脆排裹粉}', false, '{}', 0, 25.015795, 121.532295, '2026-05-03 00:50:49.787595');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '揚秦國際企業股份有限公司', '炸雞大獅', '菜頭粿', '{油,蘿蔔糕}', false, '{}', 0, 25.015795, 121.532295, '2026-05-03 00:50:54.157647');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '漢來美食股份有限公司', '漢來海港', '沙拉(美生菜)', '{"圓生菜 (進口)"}', false, '{}', 0, 25.039978, 121.54835, '2026-05-03 00:51:43.138315');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '漢來美食股份有限公司', '漢來海港', '芭樂', '{牛奶芭樂}', true, '{乳製品}', 1, 25.039978, 121.54835, '2026-05-03 00:51:43.138544');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '漢來美食股份有限公司', '漢來海港', '鮭魚生魚片', '{鮭魚}', true, '{海鮮類}', 1, 25.039978, 121.54835, '2026-05-03 00:51:43.138555');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '漢來美食股份有限公司', '漢來海港', '鮪魚生魚片', '{鮪魚}', true, '{海鮮類}', 1, 25.039978, 121.54835, '2026-05-03 00:51:43.138561');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '漢來美食股份有限公司', '漢來海港', '鯛魚生魚片', '{鯛魚}', true, '{海鮮類}', 1, 25.039978, 121.54835, '2026-05-03 00:51:43.138567');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '漢來美食股份有限公司', '漢來海港', '熟白蝦', '{熟白蝦}', true, '{海鮮類}', 1, 25.039978, 121.54835, '2026-05-03 00:51:43.138574');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '漢來美食股份有限公司', '漢來海港', '旭蟹', '{旭蟹}', true, '{海鮮類}', 1, 25.039978, 121.54835, '2026-05-03 00:51:43.13858');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '漢來美食股份有限公司', '漢來海港', '扁蟹', '{扁蟹}', true, '{海鮮類}', 1, 25.039978, 121.54835, '2026-05-03 00:51:43.138586');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '漢來美食股份有限公司', '漢來海港', '烤牛肉', '{沙朗}', false, '{}', 0, 25.039978, 121.54835, '2026-05-03 00:51:43.138592');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '漢來美食股份有限公司', '漢來海港', '炸薯條', '{帶皮薯條,沙拉油}', false, '{}', 0, 25.039978, 121.54835, '2026-05-03 00:51:43.138598');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '欣葉國際餐飲股份有限公司', '欣葉日本料理', '鮭魚生魚片', '{鮭魚}', true, '{海鮮類}', 1, 25.056238, 121.52253, '2026-05-03 00:51:45.301174');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '欣葉國際餐飲股份有限公司', '欣葉日本料理', '鮪魚生魚片', '{鮪魚}', true, '{海鮮類}', 1, 25.056238, 121.52253, '2026-05-03 00:51:45.301222');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '欣葉國際餐飲股份有限公司', '欣葉日本料理', '旗魚生魚片', '{旗魚}', true, '{海鮮類}', 1, 25.056238, 121.52253, '2026-05-03 00:51:45.30123');
INSERT INTO public.food_allergen_classification VALUES ('臺北市', '欣葉國際餐飲股份有限公司', '欣葉日本料理', '烤雞翅', '{雞翅}', false, '{}', 0, 25.056238, 121.52253, '2026-05-03 00:51:45.301238');


--
-- PostgreSQL database dump complete
--

