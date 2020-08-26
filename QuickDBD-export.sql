-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- Link to schema: https://app.quickdatabasediagrams.com/#/d/yRp4hy

CREATE TABLE "user"
(
    "id" int NOT NULL,
    "username" string NOT NULL,
    "email_address" string NOT NULL,
    "password" string NOT NULL,
    "api_key" string NOT NULL,
    "first_name" string NULL,
    "last_name" string NULL,
    "profile_img" string DEFAULT default_img.jpg NULL,
    CONSTRAINT "pk_user" PRIMARY KEY (
        "id"
     ),
    CONSTRAINT "uc_user_username" UNIQUE (
        "username"
    ),
    CONSTRAINT "uc_user_email_address" UNIQUE (
        "email_address"
    )
);

CREATE TABLE "mods"
(
    "id" int NOT NULL,
    "mod_name" string NOT NULL,
    "game_id" int NOT NULL,
    "upload_user_id" int NOT NULL,
    "posted_at" datetime NOT NULL,
    "description" string NOT NULL,
    "requirements" string NOT NULL,
    "install_instructions" string NOT NULL,
    "main_img" string DEFAULT default_mod_image.jpg NULL,
    "sub_images" list NOT NULL,
    CONSTRAINT "pk_mods" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "games"
(
    "id" int NOT NULL,
    "game_title" string NOT NULL,
    "game_genre" string NOT NULL,
    "release_year" date NOT NULL,
    "description" string NOT NULL,
    CONSTRAINT "pk_games" PRIMARY KEY (
        "id"
     )
);

ALTER TABLE "mods" ADD CONSTRAINT "fk_mods_game_id" FOREIGN KEY("game_id")
REFERENCES "games" ("id");

ALTER TABLE "mods" ADD CONSTRAINT "fk_mods_upload_user_id" FOREIGN KEY("upload_user_id")
REFERENCES "user" ("id");

