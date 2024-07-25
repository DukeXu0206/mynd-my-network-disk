LOCK TABLES `disk_rolelimit` WRITE;
INSERT INTO `disk_role` VALUES
(1, NOW(6), NOW(6), '', 'admin', 'admin', 1, 1),
(2, NOW(6), NOW(6), '', 'vip user', 'member', 1, 1),
(3, NOW(6), NOW(6), '', 'general user', 'common', 1, 1);
UNLOCK TABLES;