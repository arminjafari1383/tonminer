from django.core.management.base import BaseCommand
from miner.models import MiningPlan, SiteSetting

class Command(BaseCommand):
    help = 'Create the nine starter plans from the supplied TON Miner HTML.'
    def handle(self, *args, **options):
        plans = [(3,.5,'bronze'),(6,.75,'bronze'),(9,1,'bronze'),(20,1.5,'silver'),(40,1.75,'silver'),(60,2.3,'silver'),(100,3,'gold'),(300,3.5,'gold'),(1000,4,'gold')]
        for i,(amount,rate,tier) in enumerate(plans,1):
            MiningPlan.objects.update_or_create(amount_ton=amount, defaults={'name':f'{tier.title()} {amount} TON','tier':tier,'daily_rate_percent':rate,'active':True,'sort_order':i})
        settings = [('minimum_topup_ton','3','Minimum top-up amount (TON)'),('minimum_withdrawal_ton','100','Minimum withdrawal amount (TON)'),('free_mining_cycle_days','6','Demo cycle length in days'),('free_mining_reward_ton','1','Demo reward per cycle (TON)'),('deposit_yield_cap_multiplier','2.5','Yield cap multiplier from source HTML')]
        for key,value,description in settings: SiteSetting.objects.update_or_create(key=key, defaults={'value':value,'description':description})
        self.stdout.write(self.style.SUCCESS('Seeded 9 plans and starter settings.'))
