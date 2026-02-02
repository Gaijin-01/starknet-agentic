# Telegram DM Setup for Whale Tracker Alerts

**Issue:** Whale tracker finds arbitrage opportunities but can't deliver to Telegram.

**Root Cause:** Moltbot requires a direct DM conversation before it can send messages.

**Solution:**
1. User needs to start a DM with the Moltbot bot on Telegram
2. Send `/start` or any message to establish the conversation
3. Then alerts will come through

**Current Status:** Alerts logged to console/cron output only.

**Priority:** Medium — user quality of life
