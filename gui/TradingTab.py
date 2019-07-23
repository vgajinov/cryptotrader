import os.path
from .ControlBarWidget import ControlBarWidget
from .CandleChartWidget import CandleChartWidget
from .PlaceOrderWidget import PlaceOrderWidget
from .TradesWidget import TradesWidget
from .OrderBookGraphWidget import OrderBookGraphWidget
from .OrderBookNumericWidget import OrderBookNumericWidget
from .UserTradingWidget import UserTradingWidget
from .Separators import *
from .CustomEvents import *

from exchanges.exchangeWSFactory import ExchangeWSFactory
from exchanges.exchangeRESTFactory import ExchangeRESTFactory
from exchanges.exception import ExchangeException


class TradingTab(QtWidgets.QWidget):
    """The main trading tab that displays the candle chart, order book, trades and user order controls."""

    # set by a user
    keys_dir   = None
    exchange   = None
    pair       = None
    interval   = None

    ws_client   = None
    rest_client = None

    symbols    = None
    symbols_details  = None
    all_tickers      = None
    quote_currencies = None

    # public WS channels
    ticker_channel  = None
    book_channel    = None
    trade_channel   = None
    candles_channel = None

    # user WS channels
    orders_channel      = None
    user_trades_channel = None
    balances_channel    = None


    def __init__(self, parent):
        super(TradingTab, self).__init__()
        self.parentWidget = parent

        # left layout
        self.controlBarWidget = ControlBarWidget(self)
        self.chartWidget = CandleChartWidget()
        self.userTradingWidget = UserTradingWidget()
        self.leftLayout = QtWidgets.QVBoxLayout()
        self.leftLayout.addWidget(LineSeparator(orientation='horizontal', stroke=5))
        self.leftLayout.addWidget(self.controlBarWidget, stretch=1)
        self.leftLayout.addWidget(DoubleLineSeparator(orientation='horizontal', linecolor=COLOR_SEPARATOR,
                                                      spacecolor='rgb(0,0,0)', stroke=1, width=3))
        self.leftLayout.addWidget(self.chartWidget, stretch=20)
        self.leftLayout.addWidget(LineSeparator(orientation='horizontal', stroke=5))
        self.leftLayout.addWidget(self.userTradingWidget, stretch=8)
        self.leftLayout.addWidget(LineSeparator(orientation='horizontal', stroke=5))

        # right layout
        self.orderBookAndTradesLayout = QtWidgets.QHBoxLayout()
        self.placeOrderWidget = PlaceOrderWidget()
        self.rightLayout = QtWidgets.QVBoxLayout()
        self.rightLayout.addWidget(LineSeparator(orientation='horizontal', stroke=5))
        self.rightLayout.addLayout(self.orderBookAndTradesLayout, stretch=7)
        self.rightLayout.addWidget(LineSeparator(orientation='horizontal', stroke=5))
        self.rightLayout.addWidget(self.placeOrderWidget, stretch=2)
        self.rightLayout.addWidget(LineSeparator(orientation='horizontal', stroke=5))
        self.setupOrderBookAndTradesLayout()

        # main layout
        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainLayout.addWidget(LineSeparator(orientation='vertical', stroke=5))
        self.mainLayout.addLayout(self.leftLayout, stretch=2)
        self.mainLayout.addWidget(LineSeparator(orientation='vertical', stroke=5))
        self.mainLayout.addLayout(self.rightLayout, stretch=1)
        self.mainLayout.addWidget(LineSeparator(orientation='vertical', stroke=5))
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0, 2, 0, 0)

        self.controlBarWidget.setExchangeList(ExchangeWSFactory.get_exchanges())


    def setupOrderBookAndTradesLayout(self):
        """Creates the Order Book and the Trades layouts"""
        self.orderBookAndTradesLayout.setContentsMargins(0, 0, 0, 0)
        self.orderBookAndTradesLayout.setSpacing(0)

        self.orderBookGraphLayout   = QtWidgets.QVBoxLayout()
        self.orderBookNumericLayout = QtWidgets.QVBoxLayout()
        self.orderBookTradesLayout  = QtWidgets.QHBoxLayout()

        self.orderBookAndTradesLayout.addLayout(self.orderBookGraphLayout, stretch=4)
        self.orderBookAndTradesLayout.addWidget(LineSeparator(orientation='vertical', stroke=5))
        self.orderBookAndTradesLayout.addLayout(self.orderBookNumericLayout, stretch=6)
        self.orderBookAndTradesLayout.addWidget(LineSeparator(orientation='vertical', stroke=5))
        self.orderBookAndTradesLayout.addLayout(self.orderBookTradesLayout, stretch=5)

        # add OrderBookGraph
        self.orderBookGraph = OrderBookGraphWidget()
        self.orderBookGraphLayout.addWidget(self.orderBookGraph)
        self.orderBookGraphLayout.setContentsMargins(0, 5, 3, 0)

        # add numeric display of order book data
        self.numericOrderBookWidget = OrderBookNumericWidget()
        self.orderBookNumericLayout.addWidget(self.numericOrderBookWidget)
        self.orderBookNumericLayout.setContentsMargins(0, 5, 0, 5)

        # add trades display widget
        self.tradesTable = TradesWidget()
        self.orderBookTradesLayout.addWidget(self.tradesTable)
        self.orderBookTradesLayout.setContentsMargins(2, 5, 2, 5)


    def reset(self):
        """Resets the widget controls"""
        self.tradesTable.clear()
        self.orderBookGraph.reset()
        self.numericOrderBookWidget.clear()
        self.chartWidget.reset()


    # ------------------------------------------------------------------------------------
    # WS client interaction
    # ------------------------------------------------------------------------------------

    def _subscribe_ws_public_channels(self):
        """Subscribes to public channels for a currently set pair.
        Uses a snapshot returned by a subscribe call to initialize corresponding controls.
        """
        # subscribe to a ticker
        try:
            self.ticker_channel, snapshot = self.ws_client.subscribe_ticker(self.pair, self.update_ticker)
            if snapshot:
                last_price = snapshot[6]
                self.numericOrderBookWidget.setLastPrice(last_price)
                self.placeOrderWidget.setTicker(snapshot)

            # subscribe to an order book
            self.book_channel, snapshot = self.ws_client.subscribe_order_book(self.pair, self.update_order_book)
            if snapshot:
                self.orderBookGraph.setData(snapshot)
                self.numericOrderBookWidget.setData(snapshot)

            # subscribe to a trades channel
            self.tradesChannel, snapshot = self.ws_client.subscribe_trades(self.pair, self.update_trades)
            if snapshot:
                self.tradesTable.setData(snapshot)

            # subscribe to a candles channel
            if self.interval:
                self.candles_channel, snapshot = self.ws_client.subscribe_candles(self.pair, self.interval,
                                                                                  self.update_candles)
                if snapshot:
                    self.chartWidget.setData(snapshot)
                    self.chartWidget.updateChart()

        except ExchangeException as e:
            self.parentWidget.showExceptionPopup(e)


    def _subscribe_ws_user_channels(self):
        """Subscribes to user (authenticated) channels."""
        try:
            self.orders_channel = self.ws_client.subscribe_user_orders(self.update_user_orders)
            self.user_trades_channel = self.ws_client.subscribe_user_trades(self.update_user_trades)
            self.balances_channel = self.ws_client.subscribe_balances(self.update_balances)
        except ExchangeException as e:
            self.parentWidget.showExceptionPopup(e)

    def _unsubscribe_ws_public_channels(self):
        """Unsubscribes from currently subscribed public channels for currently selected pair."""
        try:
            self.ws_client.unsubscribe(self.ticker_channel, self.update_ticker)
            self.ws_client.unsubscribe(self.book_channel, self.update_order_book)
            self.ws_client.unsubscribe(self.tradesChannel, self.update_trades)
            if self.candles_channel:
                self.ws_client.unsubscribe(self.candles_channel, self.update_candles)
        except ExchangeException as e:
            self.parentWidget.showExceptionPopup(e)


    # ------------------------------------------------------------------------------------
    # ControlBar interaction
    # ------------------------------------------------------------------------------------

    def _clear_channels(self):
        """Clears internal channel related state"""
        self.ticker_channel  = None
        self.book_channel    = None
        self.trade_channel   = None
        self.candles_channel = None


    def exchangeChanged(self, exchange_name):
        """Handles the change of the exchange.
        Unsubscribes from all currently subscribed channels,
        disconnects from the current exchange and connect to newly selected exchange
        and subscribes to the channels for the newly selected pair.
        """
        if exchange_name == self.exchange:
            return
        self.exchange = exchange_name

        self.reset()
        self.userTradingWidget.clear()

        self.setCursor(QtCore.Qt.WaitCursor)

        try:
            # disconnect from the current exchange
            # all channels will be automatically unsubscribed
            if self.ws_client:
                self.ws_client.disconnect()
                self.ws_client = None
                self.rest_client = None

            # set the key file for the newly selected exchange
            key_file = None
            if self.keys_dir:
                key_file = os.path.join(self.keys_dir, '{}.key'.format(self.exchange.lower()))
                key_file = key_file if os.path.isfile(key_file) else None

            # connect to the new exchange and authenticate
            self.ws_client = ExchangeWSFactory.create_client(exchange_name)
            self.ws_client.connect(self.info_update)
            if key_file:
                self.ws_client.authenticate(key_file=key_file)
                self._subscribe_ws_user_channels()

            self._clear_channels()

            # create a new client for the REST requests which will handle all user (authenticated) requests
            self.rest_client = ExchangeRESTFactory.create_client(exchange_name, key_file=key_file)
            self.placeOrderWidget.setClient(self.rest_client)
            self.userTradingWidget.setClient(self.rest_client)

            # update the basic info for the new exchange
            self.quote_currencies = self.rest_client.quote_currencies()
            self.symbols = self.rest_client.symbols()
            self.symbols_details = self.rest_client.symbols_details()
            self.all_tickers = self.rest_client.all_tickers()

            # update controls to match the new exchange
            self.userTradingWidget.setSymbolDetails(self.symbols_details)
            self.controlBarWidget.setPairList(self.all_tickers, self.rest_client.quote_currencies())
            self.controlBarWidget.setIntervalList(self.rest_client.candle_intervals())
            self.controlBarWidget.setDisabled(True)
            self.pair = None
            self.interval = '1m'
            self.controlBarWidget.ctrlTime.setCurrentText(self.interval)
            self.controlBarWidget.setDisabled(False)

        except ExchangeException as e:
            self.parentWidget.showExceptionPopup(e)

        self.setCursor(QtCore.Qt.ArrowCursor)


    def pairChanged(self, pair):
        """Handles the change of the exchange pair (symbol).
        Unsubscribes from the currently subscribed public channels for a given pair
        and subscribes to the channels for the newly selected pair.
        """
        if pair == self.pair:
            return

        self.setCursor(QtCore.Qt.WaitCursor)

        if self.pair:
            self.reset()
            self._unsubscribe_ws_public_channels()
            self._clear_channels()
        self.pair = pair

        # deduce base and quote currency from a pair symbol
        for qcurrency in self.quote_currencies:
            if pair.endswith(qcurrency):
                base_currency = pair[:-len(qcurrency)]
                quote_currency = qcurrency
                break

        # get symbols details and update affected controls
        symbol_details = self.symbols_details[pair.upper()]
        self.tradesTable.setSymbolDetails(symbol_details)
        self.numericOrderBookWidget.setSymbolDetails(symbol_details)
        if self.rest_client.authenticated:
            self.placeOrderWidget.setSymbolDetails(base_currency, quote_currency, symbol_details)

        self._subscribe_ws_public_channels()

        self.setCursor(QtCore.Qt.ArrowCursor)


    def intervalChanged(self, interval):
        """Handles the change of the candles interval.
        Unsubscribes from the channel for current interval
        and subscribes to the channel for the new interval.
        """
        if interval == self.interval:
            return

        self.setCursor(QtCore.Qt.WaitCursor)

        try:
            self.interval = interval
            if self.candles_channel:
                self.ws_client.unsubscribe(self.candles_channel, self.update_candles)

            # subscribe to a candles channel
            self.candles_channel, snapshot = self.ws_client.subscribe_candles(self.pair, self.interval,
                                                                              self.update_candles)
            if snapshot:
                self.chartWidget.setData(snapshot)
                self.chartWidget.updateChart()
        except ExchangeException as e:
            self.parentWidget.showExceptionPopup(e)

        self.setCursor(QtCore.Qt.ArrowCursor)


    # ------------------------------------------------------------------------------------
    # MainWindow interactions
    # ------------------------------------------------------------------------------------

    def setKeysDirectory(self, dir_path):
        """Sets the path to the directory that holds exchange private api keys.
        The keys are expected to be named as the <exchange_name>.key,
        and exchange names should be in lower case.
        """
        self.keys_dir = dir_path
        if self.rest_client:
            key_file = os.path.join(self.keys_dir, '{}.key'.format(self.exchange.lower()))
            key_file = key_file if os.path.isfile(key_file) else None
            self.rest_client = ExchangeRESTFactory.create_client(self.exchange, key_file=key_file)
            self.ws_client.authenticate(key_file=key_file)
            self._subscribe_ws_user_channels()


    def closeConnections(self):
        """Should be called on quitting the application to properly close exchange connections."""
        if self.ws_client:
            self.ws_client.disconnect()


    # ------------------------------------------------------------------------------------
    # Event Handlers
    # ------------------------------------------------------------------------------------

    def customEvent(self, event):
        """Handles update events triggered by the exchange dispatcher
        :param event:  update event
        A dispatcher send the updates via callbacks, each of which
        only triggers appropriate event. Thus, keeping the overhead
        for the dispatcher thread low and assuring that all gui updates
        are handled by the gui thread.
        """
        if not self.isEnabled():
            return

        try:
            if event.type() == OrderBookUpdateEvent.EVENT_TYPE:
                self.orderBookGraph.setData(event.book)
                self.numericOrderBookWidget.setData(event.book)
            elif event.type() == TradesUpdateEvent.EVENT_TYPE:
                self.tradesTable.setData(event.trades)
            elif event.type() == TickerUpdateEvent.EVENT_TYPE:
                last_price = event.ticker[6]
                self.numericOrderBookWidget.setLastPrice(last_price)
                self.placeOrderWidget.setTicker(event.ticker)
            elif event.type() == CandlesUpdateEvent.EVENT_TYPE:
                self.chartWidget.setData(event.candles)
                self.chartWidget.updateChart()
            elif event.type() == OrdersUpdateEvent.EVENT_TYPE:
                self.userTradingWidget.updateOrders(event.orders)
            elif event.type() == UserTradesUpdateEvent.EVENT_TYPE:
                self.userTradingWidget.updateUserTrades(event.trades)
            elif event.type() == BalancesUpdateEvent.EVENT_TYPE:
                self.placeOrderWidget.setBalances(event.balances)
        except Exception as e:
            self.parentWidget.showExceptionPopup(e)


    # ------------------------------------------------------------------------------------
    # Update methods (callbacks from dispatcher)
    # ------------------------------------------------------------------------------------

    def update_order_book(self, data):
        """Callback handler for order book updates
        :param data:  order book update
        """
        QtWidgets.QApplication.postEvent(self, OrderBookUpdateEvent(data))

    def update_trades(self, data):
        """Callback handler for trades updates
        :param data:  trades update
        """
        QtWidgets.QApplication.postEvent(self, TradesUpdateEvent(data))

    def update_ticker(self, data):
        """Callback handler for ticker updates
        :param data:  ticker update
        """
        QtWidgets.QApplication.postEvent(self, TickerUpdateEvent(data))

    def update_candles(self, data):
        """Callback handler for candles updates
        :param data:  candles update
        """
        QtWidgets.QApplication.postEvent(self, CandlesUpdateEvent(data))

    def update_user_orders(self, data):
        """Callback handler for user orders updates
        :param data:  user orders update
        """
        QtWidgets.QApplication.postEvent(self, OrdersUpdateEvent(data))

    def update_user_trades(self, data):
        """Callback handler for user trades updates
        :param data:  user trades update
        """
        QtWidgets.QApplication.postEvent(self, UserTradesUpdateEvent(data))

    def update_balances(self, data):
        """Callback handler for balances updates
        :param data:  balances update
        """
        QtWidgets.QApplication.postEvent(self, BalancesUpdateEvent(data))

    # handle info messages
    def info_update(self, data):
        """Callback handler for info messages
        :param data:  info message
        """
        pass

