module default {
    type User {
        property full_name -> str;
        required property email -> str {
            constraint exclusive;
        };
        required property hashed_password -> str;
        property is_superuser -> bool {
            default := false;
        }
        property is_active -> bool {
            default := true;
        }
        index on (.full_name);
        index on (.email);
    }
    type Item {
        property title -> str;
        property description -> str;
        link owner -> User;
        index on (.title);
        index on (.description);
    }
}
