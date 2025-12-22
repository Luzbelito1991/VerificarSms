BEGIN TRANSACTION;
CREATE TABLE password_reset_tokens (
	id INTEGER NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	token VARCHAR(100) NOT NULL, 
	expiracion DATETIME NOT NULL, 
	usado INTEGER, 
	fecha_creacion DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
);
INSERT INTO "password_reset_tokens" VALUES(1,7,'0y7x2l0H_SuCLYDCn7BcKzA12pWauZ0lVpjYk2DYlNk','2025-12-22 15:46:53.421600',0,'2025-12-22 13:46:53.422451');
INSERT INTO "password_reset_tokens" VALUES(2,7,'Dv1aRIUcdd8Ed7dU3Wy3Ev3vQXHLJt50wt2-Hjgfn94','2025-12-22 15:46:55.725231',0,'2025-12-22 13:46:55.725478');
CREATE TABLE sucursales (
            codigo VARCHAR(10) PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL
        );
INSERT INTO "sucursales" VALUES('389','Rincón Deportivo');
INSERT INTO "sucursales" VALUES('123','Mmya');
INSERT INTO "sucursales" VALUES('150','Caution');
INSERT INTO "sucursales" VALUES('198','Ferlor');
INSERT INTO "sucursales" VALUES('206','Calzado René');
INSERT INTO "sucursales" VALUES('211','Calzados Alonso');
CREATE TABLE usuarios (
	id INTEGER NOT NULL, 
	usuario VARCHAR(50) NOT NULL, 
	hash_password VARCHAR(128) NOT NULL, 
	rol VARCHAR(20) NOT NULL, email VARCHAR(255), 
	PRIMARY KEY (id)
);
INSERT INTO "usuarios" VALUES(3,'Fernando','$2b$12$oISX8YvhoH0ym8dniCUNbegv6UzeonsBkTvCI1ntDTkjy3B2yVUya','admin',NULL);
INSERT INTO "usuarios" VALUES(4,'Andrea','$2b$12$QrLwzhLxrE69ARExp8JRHuvIKweLIZCBMK66PRk/yspKaDE1h4kvm','operador',NULL);
INSERT INTO "usuarios" VALUES(5,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9','admin',NULL);
INSERT INTO "usuarios" VALUES(6,'fernando','03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4','admin',NULL);
INSERT INTO "usuarios" VALUES(7,'Nora','$2b$12$7XaYPz4eJV0Ya4lwQHchfOoxtwBGKG0ddCIeAQQM5QuoB9LmDv3Vm','operador','vallefernando884@gmail.com');
CREATE TABLE verificaciones (
	id INTEGER NOT NULL, 
	person_id VARCHAR, 
	phone_number VARCHAR NOT NULL, 
	merchant_code VARCHAR, 
	merchant_name VARCHAR, 
	verification_code VARCHAR, 
	fecha DATETIME, 
	usuario_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id)
);
INSERT INTO "verificaciones" VALUES(3,'14300166','3815899445','777','Lules','5525','2025-12-20 12:49:01.652129',4);
INSERT INTO "verificaciones" VALUES(4,'14300166','3815899445','561','Oregon Jeans','6255','2025-12-20 12:49:25.563325',4);
INSERT INTO "verificaciones" VALUES(5,'36049884','3814123693','777','Lules','6566','2025-12-22 09:17:50.697540',3);
INSERT INTO "verificaciones" VALUES(6,'36049884','3814123693','776','Limite Deportes Alberdi','9259','2025-12-22 09:47:34.078769',4);
INSERT INTO "verificaciones" VALUES(7,'14300166','3814588888','776','Limite Deportes Alberdi','7644','2025-12-22 11:23:48.365675',6);
CREATE INDEX ix_usuarios_id ON usuarios (id);
CREATE UNIQUE INDEX ix_usuarios_usuario ON usuarios (usuario);
CREATE INDEX ix_verificaciones_id ON verificaciones (id);
CREATE INDEX ix_verificaciones_merchant_code ON verificaciones (merchant_code);
CREATE INDEX ix_verificaciones_person_id ON verificaciones (person_id);
CREATE INDEX ix_verificaciones_verification_code ON verificaciones (verification_code);
CREATE INDEX ix_password_reset_tokens_id ON password_reset_tokens (id);
CREATE UNIQUE INDEX ix_password_reset_tokens_token ON password_reset_tokens (token);
COMMIT;
