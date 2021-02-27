from typing import Dict, List, NamedTuple, Sequence, Tuple

from django.core.management.base import BaseCommand

from django_celery_beat.models import IntervalSchedule, PeriodicTask

from gnosis.eth import EthereumClientProvider
from gnosis.eth.ethereum_client import EthereumNetwork

from ...models import ProxyFactory, SafeMasterCopy


class CeleryTaskConfiguration(NamedTuple):
    name: str
    description: str
    interval: int
    period: str

    def create_task(self) -> Tuple[PeriodicTask, bool]:
        interval, _ = IntervalSchedule.objects.get_or_create(every=self.interval, period=self.period)
        periodic_task, created = PeriodicTask.objects.get_or_create(task=self.name,
                                                                    defaults={
                                                                        'name': self.description,
                                                                        'interval': interval
                                                                    })
        if periodic_task.interval != interval:
            periodic_task.interval = interval
            periodic_task.save(update_fields=['interval'])

        return periodic_task, created


TASKS = [
    CeleryTaskConfiguration('safe_transaction_service.history.tasks.index_internal_txs_task',
                            'Index Internal Txs', 13, IntervalSchedule.SECONDS),
    # CeleryTaskConfiguration('safe_transaction_service.history.tasks.index_new_proxies_task',
    #                        'Index new Proxies', 15, IntervalSchedule.SECONDS),
    CeleryTaskConfiguration('safe_transaction_service.history.tasks.index_erc20_events_task',
                            'Index ERC20 Events', 14, IntervalSchedule.SECONDS),
    CeleryTaskConfiguration('safe_transaction_service.history.tasks.process_decoded_internal_txs_task',
                            'Process Internal Txs', 2, IntervalSchedule.MINUTES),
    CeleryTaskConfiguration('safe_transaction_service.history.tasks.check_reorgs_task',
                            'Check Reorgs', 3, IntervalSchedule.MINUTES),
    CeleryTaskConfiguration('safe_transaction_service.tokens.tasks.fix_pool_tokens_task',
                            'Fix Pool Token Names', 1, IntervalSchedule.HOURS),
]

MASTER_COPIES: Dict[EthereumNetwork, List[Tuple[str, int, str]]] = {
    # changing mastercopy contract addresses, all to opera testnet deployed contracts
    EthereumNetwork.MAINNET: [
        ('0xe3d4Af0e46Aa207222bC6FC11652dDF68eBF1d15', 367377, '1.2.0'),
        ('0xe3d4Af0e46Aa207222bC6FC11652dDF68eBF1d15', 367377, '1.1.1'),
        ('0xe3d4Af0e46Aa207222bC6FC11652dDF68eBF1d15', 367377, '1.1.0'),
        ('0xe3d4Af0e46Aa207222bC6FC11652dDF68eBF1d15', 367377, '1.0.0'),
        ('0xe3d4Af0e46Aa207222bC6FC11652dDF68eBF1d15', 367377, '0.1.0'),
        ('0xe3d4Af0e46Aa207222bC6FC11652dDF68eBF1d15', 367377, '0.0.2'),
    ],
    # EthereumNetwork.RINKEBY: [
    #     ('0xe3d4Af0e46Aa207222bC6FC11652dDF68eBF1d15', 367377, '1.2.0'),
    #     ('0xe3d4Af0e46Aa207222bC6FC11652dDF68eBF1d15', 367377, '1.1.1'),
    #     ('0xe3d4Af0e46Aa207222bC6FC11652dDF68eBF1d15', 367377, '1.1.0'),
    #     ('0xe3d4Af0e46Aa207222bC6FC11652dDF68eBF1d15', 367377, '1.0.0'),
    #     ('0xe3d4Af0e46Aa207222bC6FC11652dDF68eBF1d15', 367377, '0.1.0'),
    #     ('0xe3d4Af0e46Aa207222bC6FC11652dDF68eBF1d15', 367377, '0.0.2'),
    # ],
    # EthereumNetwork.GOERLI: [
    #     ('0x6851D6fDFAfD08c0295C392436245E5bc78B0185', 2930373, '1.2.0'),
    #     ('0x34CfAC646f301356fAa8B21e94227e3583Fe3F5F', 1798663, '1.1.1'),
    #     ('0xaE32496491b53841efb51829d6f886387708F99B', 1631488, '1.1.0'),
    #     ('0xb6029EA3B2c51D09a50B53CA8012FeEB05bDa35A', 319108, '1.0.0'),
    #     ('0x8942595A2dC5181Df0465AF0D7be08c8f23C93af', 34096, '0.1.0'),
    # ],
    # EthereumNetwork.KOVAN: [
    #     ('0x6851D6fDFAfD08c0295C392436245E5bc78B0185', 19242615, '1.2.0'),
    #     ('0x34CfAC646f301356fAa8B21e94227e3583Fe3F5F', 15366145, '1.1.1'),
    #     ('0xaE32496491b53841efb51829d6f886387708F99B', 14740724, '1.1.0'),
    #     ('0xb6029EA3B2c51D09a50B53CA8012FeEB05bDa35A', 10638132, '1.0.0'),
    #     ('0x8942595A2dC5181Df0465AF0D7be08c8f23C93af', 9465686, '0.1.0'),
    # ],
    # EthereumNetwork.XDAI: [
    #     ('0x6851D6fDFAfD08c0295C392436245E5bc78B0185', 10612049, '1.2.0'),
    #     ('0x34CfAC646f301356fAa8B21e94227e3583Fe3F5F', 10045292, '1.1.1'),
    #     ('0x2CB0ebc503dE87CFD8f0eCEED8197bF7850184ae', 12529466, '1.1.1-Circles'),
    # ],
    # EthereumNetwork.ENERGY_WEB_CHAIN: [
    #     ('0x6851D6fDFAfD08c0295C392436245E5bc78B0185', 6398655, '1.2.0'),
    #     ('0x34CfAC646f301356fAa8B21e94227e3583Fe3F5F', 6399212, '1.1.1'),
    # ],
    # EthereumNetwork.VOLTA: [
    #     ('0x6851D6fDFAfD08c0295C392436245E5bc78B0185', 6876086, '1.2.0'),
    #     ('0x34CfAC646f301356fAa8B21e94227e3583Fe3F5F', 6876642, '1.1.1'),
    # ]

}

PROXY_FACTORIES: Dict[EthereumNetwork, List[Tuple[str, int]]] = {
    # changing proxyfactory contract address, all -> opera testnet deployed contract' address
    EthereumNetwork.MAINNET: [
        ('0x5eAa96A55e703BD410DCdc300683a05951080218', 369855),  # v1.1.1
        ('0x5eAa96A55e703BD410DCdc300683a05951080218', 369855),  # v1.1.0
        ('0x5eAa96A55e703BD410DCdc300683a05951080218', 369855),  # v1.0.0
    ],
    # EthereumNetwork.RINKEBY: [
    #     ('0x5eAa96A55e703BD410DCdc300683a05951080218', 369855),
    #     ('0x5eAa96A55e703BD410DCdc300683a05951080218', 369855),
    #     ('0x5eAa96A55e703BD410DCdc300683a05951080218', 369855),
    # ],
    # EthereumNetwork.GOERLI: [
    #     ('0x76E2cFc1F5Fa8F6a5b3fC4c8F4788F0116861F9B', 1798666),
    #     ('0x50e55Af101C777bA7A1d560a774A82eF002ced9F', 1631491),
    #     ('0x12302fE9c02ff50939BaAaaf415fc226C078613C', 312509),
    # ],
    # EthereumNetwork.KOVAN: [
    #     ('0x76E2cFc1F5Fa8F6a5b3fC4c8F4788F0116861F9B', 15366151),
    #     ('0x50e55Af101C777bA7A1d560a774A82eF002ced9F', 14740731),
    #     ('0x12302fE9c02ff50939BaAaaf415fc226C078613C', 10629898),
    # ],
    # EthereumNetwork.XDAI: [
    #     ('0x76E2cFc1F5Fa8F6a5b3fC4c8F4788F0116861F9B', 10045327),
    # ],
    # EthereumNetwork.ENERGY_WEB_CHAIN: [
    #     ('0x76E2cFc1F5Fa8F6a5b3fC4c8F4788F0116861F9B', 6399239),
    # ],
    # EthereumNetwork.VOLTA: [
    #     ('0x76E2cFc1F5Fa8F6a5b3fC4c8F4788F0116861F9B', 6876681),
    # ]
}


class Command(BaseCommand):
    help = 'Setup Transaction Service Required Tasks'

    def handle(self, *args, **options):
        # for task in TASKS:
        #     _, created = task.create_task()
        #     if created:
        #         self.stdout.write(self.style.SUCCESS('Created Periodic Task %s' % task.name))
        #     else:
        #         self.stdout.write(self.style.SUCCESS('Task %s was already created' % task.name))

        # self.stdout.write(self.style.SUCCESS('Setting up Safe Contract Addresses'))
        
        # change to set up for opera test network
        
            for task in self.tasks:
            _, created = task.create_task()
            if created:
                self.stdout.write(self.style.SUCCESS('Created Periodic Task %s' % task.name))
            else:
                self.stdout.write(self.style.SUCCESS('Task %s was already created' % task.name))

        self.stdout.write(self.style.SUCCESS('Setting up Safe Contract Addresses'))
        self.setup_my_network()
        
        ethereum_client = EthereumClientProvider()
        # ethereum_network = ethereum_client.get_network() -- this is for ethereum blockchain
        # if ethereum_network in MASTER_COPIES:
        #     self.stdout.write(self.style.SUCCESS(f'Setting up {ethereum_network.name} safe addresses'))
        #     self._setup_safe_master_copies(MASTER_COPIES[ethereum_network])
        # if ethereum_network in PROXY_FACTORIES:
        #     self.stdout.write(self.style.SUCCESS(f'Setting up {ethereum_network.name} proxy factory addresses'))
        #     self._setup_safe_proxy_factories(PROXY_FACTORIES[ethereum_network])

        # if not (ethereum_network in MASTER_COPIES and ethereum_network in PROXY_FACTORIES):
        #     self.stdout.write(self.style.WARNING('Cannot detect a valid ethereum-network'))
        
        # changing for opera test network
        # ethereum_network_id = ethereum_client.w3.net.version
        # if ethereum_network in MASTER_COPIES:
        #     self.stdout.write(self.style.SUCCESS(f'Setting up {ethereum_network.name} safe addresses'))
        #     self._setup_safe_master_copies(MASTER_COPIES[ethereum_network])
        # if ethereum_network in PROXY_FACTORIES:
        #     self.stdout.write(self.style.SUCCESS(f'Setting up {ethereum_network.name} proxy factory addresses'))
        #     self._setup_safe_proxy_factories(PROXY_FACTORIES[ethereum_network])

        # if not (ethereum_network in MASTER_COPIES and ethereum_network in PROXY_FACTORIES):
        #     self.stdout.write(self.style.WARNING('Cannot detect a valid ethereum-network'))
        
        ethereum_network_id = ethereum_client.w3.net.version
        try:
            self.stdout.write(self.style.SUCCESS(f'Setting up {4002} safe addresses'))
            self._setup_safe_master_copies(ethereum_network_id)
        except:
            self.stdout.write(self.style.WARNING('Error in MASTER COPIES CREATION'))
            
        try:
            self.stdout.write(self.style.SUCCESS(f'Setting up {ethereum_network.name} proxy factory addresses'))
            self._setup_safe_proxy_factories(ethereum_network_id)
        except:
            self.stdout.write(self.style.WARNING('Error in PROXY FACTORIES CREATION'))

    def _setup_safe_master_copies(self, safe_master_copies: Sequence[Tuple[str, int, str]]):
        for address, initial_block_number, version in safe_master_copies:
            safe_master_copy, _ = SafeMasterCopy.objects.get_or_create(
                address=address,
                defaults={
                    'initial_block_number': initial_block_number,
                    'tx_block_number': initial_block_number,
                    'version': version,
                }
            )
            if safe_master_copy.version != version:
                safe_master_copy.version = version
                safe_master_copy.save(update_fields=['version'])

    def _setup_safe_proxy_factories(self, safe_proxy_factories: Sequence[Tuple[str, int]]):
        for address, initial_block_number in safe_proxy_factories:
            ProxyFactory.objects.get_or_create(address=address,
                                               defaults={
                                                   'initial_block_number': initial_block_number,
                                                   'tx_block_number': initial_block_number,
                                               })

    # manually setting up the environment
    def setup_my_network(self):
        SafeMasterCopy.objects.get_or_create(address='0xe3d4Af0e46Aa207222bC6FC11652dDF68eBF1d15',
                                             defaults={
                                                 'initial_block_number': 367377,
                                                 'tx_block_number': 367377,
                                             })

        ProxyFactory.objects.get_or_create(address='0x5eAa96A55e703BD410DCdc300683a05951080218',
                                           defaults={
                                               'initial_block_number': 369855,
                                               'tx_block_number': 369855,
                                           })
