# Configure only after reconciling against the complete source and approved business rules.
FREE_TH = 10
FREE_CYCLE_SECONDS = 6 * 24 * 60 * 60
FREE_CYCLE_REWARD_TON = "1.0000000000000000"
DEPOSIT_YIELD_CAP_MULTIPLIER = "2.5"
MIN_TOPUP_TON = "3"
MIN_WITHDRAW_TON = "100"

# Conservative configurable tiers. Validate exact tier amounts/rates against source before launch.
TIERS = [
    {"code":"bronze-3","name":"Bronze","amount":"3","daily_rate_percent":"0.5"},
    {"code":"bronze-6","name":"Bronze","amount":"6","daily_rate_percent":"0.75"},
    {"code":"bronze-9","name":"Bronze","amount":"9","daily_rate_percent":"1"},
    {"code":"silver-20","name":"Silver","amount":"20","daily_rate_percent":"1.5"},
    {"code":"silver-40","name":"Silver","amount":"40","daily_rate_percent":"1.75"},
    {"code":"silver-60","name":"Silver","amount":"60","daily_rate_percent":"2.3"},
    {"code":"gold-100","name":"Gold","amount":"100","daily_rate_percent":"3"},
    {"code":"gold-300","name":"Gold","amount":"300","daily_rate_percent":"3.5"},
    {"code":"gold-1000","name":"Gold","amount":"1000","daily_rate_percent":"4"},
]
