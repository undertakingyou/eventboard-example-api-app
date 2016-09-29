drop table if exists credentials;
create table credentials (
    id integer primary key autoincrement,
    client_id text not null,
    client_secret text not null,
    access_token text not null,
    token_type text,
    expires_in integer not null,
    update_datetime integer,
    refresh_token text not null
);
INSERT INTO credentials (client_id, client_secret, access_token, token_type, expires_in, refresh_token) VALUES (
    /* Here we want the above values, as obtained through an OAUTH2.0 initial session. A great tool for this is PostMan */
    'example_client_id', /* Change to actual EB client ID */
    'example_client_secret', /* Change to actual EB Client Secret */
    'example_access_token', /* Change to actual access token */
    'Bearer', /* token_type, Will likely be bearer, but change as needed */
    36000, /* expires_in. Int value in seconds, default is shown */
    'example_refresh_token' /* Change to te actual refresh token */ 
);