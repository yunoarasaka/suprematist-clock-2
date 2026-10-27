# AppArmor profile for Electron on Ubuntu 24.04+ / 26+
# (apparmor_restrict_unprivileged_userns). Bundled into .deb/.rpm by
# electron-builder ≥26 and installed via after-install to
# /etc/apparmor.d/${executable}. Allows userns so Chromium sandbox works
# without --no-sandbox. AppImage cannot auto-attach this (path moves).
abi <abi/4.0>,
include <tunables/global>

profile "${executable}" "/opt/${sanitizedProductName}/${executable}" flags=(unconfined) {
  userns,

  # Site-specific additions and overrides. See local/README for details.
  include if exists <local/${executable}>
}
