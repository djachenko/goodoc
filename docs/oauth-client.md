# Getting `credentials.json`

goodoc needs an OAuth client of type **Desktop app** from a Google Cloud project you
control. The wizard asks for the JSON file Google gives you for that client.

---

## From scratch

1. [Create a project](https://console.cloud.google.com/projectcreate) — any name, no
   organization needed
2. Enable the [Google Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com)
   → **Enable**
3. Fill in [Branding](https://console.cloud.google.com/auth/branding):
   app name, your email as support and developer contact
4. Set [Audience](https://console.cloud.google.com/auth/audience) to **External**,
   add your own account under **Test users**
5. Press **Publish app** on the same page — in testing mode Google expires the refresh
   token after 7 days
6. Create the client in [Credentials](https://console.cloud.google.com/apis/credentials):
   **+ Create Credentials → OAuth client ID**, application type **Desktop app**
7. Download the JSON from the dialog shown right after creation — it lands in
   `~/Downloads/client_secret_*.json`

Check the project picker in the top bar before each step — the console likes to switch
projects on you.

**Publishing is not verification.** It needs no review, no approval, no domain, no privacy
policy — the switch takes effect immediately. Google only requires verification for
sensitive and restricted scopes; goodoc asks for `drive.file`, which is neither. It grants
access to files the app itself created, and nothing else in your Drive.

---

## Existing client

Google no longer lets you view or download the secret of a client after creation, so the
[Credentials](https://console.cloud.google.com/apis/credentials) list has no download
button — only ✏️ and 🗑. Add a second secret instead: the client ID stays the same, so
tokens already issued keep working.

1. Open the client from [Clients](https://console.cloud.google.com/auth/clients) —
   click its name; type must be **Desktop**
2. **Client secrets → Add secret**
3. Download the JSON from that dialog — the secret is shown once
4. Check that the [Google Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com)
   is enabled in this project
5. Check [Audience](https://console.cloud.google.com/auth/audience) — if it still says
   Testing, press **Publish app**
6. Run goodoc; once it works, disable and delete the old secret in
   [Clients](https://console.cloud.google.com/auth/clients)

Creating a fresh Desktop client (steps 6–7 above) is equally fine — old tokens are then
invalid, clear them with `goodoc logout`.

---

## Where it goes

The wizard copies the file to `~/.config/goodoc/credentials.json`. The token it obtains
afterwards is stored next to it as `token.json`.
