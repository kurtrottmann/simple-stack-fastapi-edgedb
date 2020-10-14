module default {
    type User {
        required property email -> str {
            constraint exclusive;
        };
        required property hashed_password -> str;
        property full_name -> str;
        property is_superuser -> bool {
            default := false;
        }
        property is_active -> bool {
            default := true;
        }
        property num_items := count(.<owner[IS Item]);
        multi link items := .<owner[IS Item];
        index on (.full_name);
    }
    type Item {
        required property title -> str;
        property description -> str;
        required link owner -> User;
        index on (.title);
        index on (.description);
    }
}
