import pytest

from rotkehlchen.accounting.mixins.event import AccountingEventType
from rotkehlchen.accounting.pnl import PNL, PnlTotals
from rotkehlchen.assets.asset import EthereumToken
from rotkehlchen.constants import ONE, ZERO
from rotkehlchen.constants.assets import A_BTC, A_ETH, A_EUR
from rotkehlchen.exchanges.data_structures import Trade
from rotkehlchen.fval import FVal
from rotkehlchen.tests.utils.accounting import (
    accounting_history_process,
    check_pnls_and_csv,
    history1,
)
from rotkehlchen.tests.utils.constants import A_CHF, A_XMR
from rotkehlchen.tests.utils.history import prices
from rotkehlchen.tests.utils.messages import no_message_errors
from rotkehlchen.types import Location, TradeType


@pytest.mark.parametrize('mocked_price_queries', [prices])
def test_simple_accounting(accountant):
    accounting_history_process(accountant, 1436979735, 1495751688, history1)
    no_message_errors(accountant.msg_aggregator)
    expected_pnls = PnlTotals({
        AccountingEventType.TRADE: PNL(taxable=FVal('559.6947154'), free=ZERO),
        AccountingEventType.FEE: PNL(taxable=FVal('-0.23886813'), free=ZERO),
    })
    check_pnls_and_csv(accountant, expected_pnls)


@pytest.mark.parametrize('mocked_price_queries', [prices])
def test_selling_crypto_bought_with_crypto(accountant):
    history = [
        Trade(
            timestamp=1446979735,
            location=Location.EXTERNAL,
            base_asset=A_BTC,
            quote_asset=A_EUR,
            trade_type=TradeType.BUY,
            amount=FVal(82),
            rate=FVal('268.678317859'),
            fee=None,
            fee_currency=None,
            link=None,
        ), Trade(
            timestamp=1449809536,  # cryptocompare hourly BTC/EUR price: 386.175
            location=Location.POLONIEX,
            base_asset=A_XMR,  # cryptocompare hourly XMR/EUR price: 0.39665
            quote_asset=A_BTC,
            trade_type=TradeType.BUY,
            amount=FVal(375),
            rate=FVal('0.0010275'),
            fee=FVal('0.9375'),
            fee_currency=A_XMR,
            link=None,
        ), Trade(
            timestamp=1458070370,  # cryptocompare hourly rate XMR/EUR price: 1.0443027675
            location=Location.KRAKEN,
            base_asset=A_XMR,
            quote_asset=A_EUR,
            trade_type=TradeType.SELL,
            amount=FVal(45),
            rate=FVal('1.0443027675'),
            fee=FVal('0.117484061344'),
            fee_currency=A_XMR,
            link=None,
        ),
    ]
    accounting_history_process(accountant, 1436979735, 1495751688, history)
    no_message_errors(accountant.msg_aggregator)
    # Make sure buying XMR with BTC also creates a BTC sell
    sells = accountant.pots[0].cost_basis.get_events(A_BTC).spends
    assert len(sells) == 1
    assert sells[0].timestamp == 1449809536
    assert sells[0].amount.is_close(FVal('0.3853125'))
    assert sells[0].rate.is_close(FVal('386.03406326'))

    expected_pnls = PnlTotals({
        AccountingEventType.TRADE: PNL(taxable=FVal('74.3118704999540625'), free=ZERO),
        AccountingEventType.FEE: PNL(taxable=FVal('-0.419658351381311222'), free=ZERO),
    })
    check_pnls_and_csv(accountant, expected_pnls)


@pytest.mark.parametrize('mocked_price_queries', [prices])
def test_buy_event_creation(accountant):
    history = [
        Trade(
            timestamp=1476979735,
            location=Location.KRAKEN,
            base_asset=A_BTC,
            quote_asset=A_EUR,
            trade_type=TradeType.BUY,
            amount=FVal(5),
            rate=FVal('578.505'),
            fee=FVal('0.0012'),
            fee_currency=A_BTC,
            link=None,
        ), Trade(
            timestamp=1476979735,
            location=Location.KRAKEN,
            base_asset=A_BTC,
            quote_asset=A_EUR,
            trade_type=TradeType.BUY,
            amount=FVal(5),
            rate=FVal('578.505'),
            fee=FVal('0.0012'),
            fee_currency=A_EUR,
            link=None,
        ),
    ]
    accounting_history_process(accountant, 1436979735, 1519693374, history)
    no_message_errors(accountant.msg_aggregator)
    buys = accountant.pots[0].cost_basis.get_events(A_BTC).acquisitions
    assert len(buys) == 2
    assert buys[0].amount == FVal(5)
    assert buys[0].timestamp == 1476979735
    assert buys[0].rate.is_close('578.6438412')  # (578.505 * 5 + 0.0012 * 578.505)/5

    assert buys[1].amount == FVal(5)
    assert buys[1].timestamp == 1476979735
    assert buys[1].rate == FVal('578.50524')  # (578.505 * 5 + 0.0012)/5


@pytest.mark.parametrize('mocked_price_queries', [prices])
def test_no_corresponding_buy_for_sell(accountant):
    """Test that if there is no corresponding buy for a sell, the entire sell counts as profit"""
    history = [Trade(
        timestamp=1476979735,
        location=Location.KRAKEN,
        base_asset=A_BTC,
        quote_asset=A_EUR,
        trade_type=TradeType.SELL,
        amount=FVal(1),
        rate=FVal('2519.62'),
        fee=FVal('0.02'),
        fee_currency=A_EUR,
        link=None,
    )]
    accounting_history_process(
        accountant=accountant,
        start_ts=1436979735,
        end_ts=1519693374,
        history_list=history,
    )

    expected_pnls = PnlTotals({
        AccountingEventType.TRADE: PNL(taxable=FVal('2519.62'), free=ZERO),
        AccountingEventType.FEE: PNL(taxable=FVal('-0.02'), free=ZERO),
    })
    check_pnls_and_csv(accountant, expected_pnls)


@pytest.mark.parametrize('mocked_price_queries', [prices])
def test_accounting_works_for_empty_history(accountant):
    history = []
    accounting_history_process(
        accountant=accountant,
        start_ts=1436979735,
        end_ts=1519693374,
        history_list=history,
    )
    no_message_errors(accountant.msg_aggregator)
    expected_pnls = PnlTotals()
    check_pnls_and_csv(accountant, expected_pnls)


@pytest.mark.parametrize('db_settings', [{
    'taxfree_after_period': -1,
}])
@pytest.mark.parametrize('mocked_price_queries', [prices])
def test_sell_fiat_for_crypto(accountant):
    """
    Test for https://github.com/rotki/rotki/issues/2993
    Make sure that selling fiat for crypto does not give warnings due to
    inability to trace the source of the sold fiat.
    """
    history = [
        Trade(
            timestamp=1446979735,
            location=Location.KRAKEN,
            base_asset=A_EUR,
            quote_asset=A_BTC,
            trade_type=TradeType.SELL,
            amount=FVal(2000),
            rate=FVal('0.002'),
            fee=FVal('0.0012'),
            fee_currency=A_EUR,
            link=None,
        ), Trade(
            # Selling 500 CHF for ETH with 0.004 CHF/ETH. + 0.02 EUR
            # That means 2 ETH for 500 CHF + 0.02 EUR -> with 1.001 CHF/EUR ->
            # (500*1.001 + 0.02)/2 -> 250.26 EUR per ETH
            timestamp=1496979735,
            location=Location.KRAKEN,
            base_asset=A_CHF,
            quote_asset=A_ETH,
            trade_type=TradeType.SELL,
            amount=FVal(500),
            rate=FVal('0.004'),
            fee=FVal('0.02'),
            fee_currency=A_EUR,
            link=None,
        ), Trade(
            timestamp=1506979735,
            location=Location.KRAKEN,
            base_asset=A_ETH,
            quote_asset=A_EUR,
            trade_type=TradeType.SELL,
            amount=ONE,
            rate=FVal(25000),
            fee=FVal('0.02'),
            fee_currency=A_EUR,
            link=None,
        ),
    ]
    accounting_history_process(
        accountant=accountant,
        start_ts=1436979735,
        end_ts=1519693374,
        history_list=history,
    )
    no_message_errors(accountant.msg_aggregator)
    expected_pnls = PnlTotals({
        AccountingEventType.TRADE: PNL(taxable=FVal('24749.74'), free=ZERO),
        AccountingEventType.FEE: PNL(taxable=FVal('-0.0412'), free=ZERO),
    })
    check_pnls_and_csv(accountant, expected_pnls)


@pytest.mark.parametrize('should_mock_price_queries', [False])
def test_asset_and_price_not_found_in_history_processing(accountant):
    """
    Make sure that in history processing if no price is found for a trade it's skipped
    and an error is logged.

    Regression for https://github.com/rotki/rotki/issues/432
    """
    fgp = EthereumToken('0xd9A8cfe21C232D485065cb62a96866799d4645f7')
    history = [Trade(
        timestamp=1492685761,
        location=Location.KRAKEN,
        base_asset=fgp,
        quote_asset=A_BTC,
        trade_type=TradeType.BUY,
        amount=FVal('2.5'),
        rate=FVal(.11000),
        fee=FVal('0.15'),
        fee_currency=fgp,
        link=None,
    )]
    accounting_history_process(
        accountant,
        start_ts=0,
        end_ts=1514764799,  # 31/12/2017
        history_list=history,
    )
    errors = accountant.msg_aggregator.consume_errors()
    assert len(errors) == 2
    assert 'No documented acquisition found for BTC' in errors[0]
    assert 'due to inability to find a price at that point in time' in errors[1]
