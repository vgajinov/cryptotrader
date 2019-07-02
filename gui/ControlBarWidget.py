from .Overlays import OverlayFactory
from .Indicators import IndicatorFactory
from .CustomComboBoxes import *


# ------------------------------------------------------------------------------------
# ControlBarWidget
# ------------------------------------------------------------------------------------

class ControlBarWidget(QtWidgets.QWidget):
    """A Widget with controls for selecting the exchange, pair and time interval"""
    itemChangedByUser = True

    def __init__(self, parent):
        super(ControlBarWidget, self).__init__()

        self.ctrlExchange = ControlComboBox()
        self.ctrlExchange.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.ctrlExchange.setObjectName('exchangeCombo')

        self.ctrlPair = ControlComboBox(15)
        self.ctrlPair.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.ctrlPair.setObjectName('pairCombo')

        self.ctrlTime = ControlComboBox()
        self.ctrlTime.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.ctrlTime.setObjectName('timeCombo')

        self.ctrlOverlay = CheckableControlComboBox()
        self.ctrlOverlay.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.ctrlOverlay.setObjectName('overlayCombo')

        self.ctrlIndicator = CheckableControlComboBox()
        self.ctrlIndicator.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.ctrlIndicator.setObjectName('indicatorCombo')

        mainLayout = QtWidgets.QHBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        ctrlLeftLayout = QtWidgets.QHBoxLayout()
        ctrlRightLayout = QtWidgets.QHBoxLayout()

        ctrlLeftLayout.addWidget(self.ctrlExchange)
        ctrlLeftLayout.addWidget(self.ctrlPair)
        ctrlLeftLayout.addWidget(self.ctrlTime)
        ctrlLeftLayout.setSpacing(10)
        ctrlLeftLayout.setContentsMargins(5, 5, 5, 5)
        ctrlLeftLayout.setAlignment(QtCore.Qt.AlignLeft)

        ctrlRightLayout.addWidget(self.ctrlOverlay)
        ctrlRightLayout.addWidget(self.ctrlIndicator)
        ctrlRightLayout.setSpacing(10)
        ctrlRightLayout.setContentsMargins(5, 5, 5, 5)
        ctrlRightLayout.setAlignment(QtCore.Qt.AlignRight)

        mainLayout.addLayout(ctrlLeftLayout)
        mainLayout.addLayout(ctrlRightLayout)

        self.setControls()


    def setControls(self):
        # Initialize exchange combo
        self.ctrlExchange.addItem('EXCHANGE')

        # Initialize interval combo
        self.ctrlTime.setView(QtWidgets.QListView())
        self.ctrlTime.addItem('TIME')
        self.ctrlTime.setEnabled(False)

        self.setPairCombo()
        self.setOverlayCombo()
        self.setIndicatorCombo()

        # connect event handlers
        self.ctrlExchange.currentTextChanged.connect(self.exchangeChanged)
        self.ctrlPair.currentTextChanged.connect(self.pairChanged)
        self.ctrlTime.currentTextChanged.connect(self.intervalChanged)
        self.ctrlOverlay.model().itemChanged.connect(self.overlayChanged)
        self.ctrlIndicator.model().itemChanged.connect(self.indicatorChanged)


    def setPairCombo(self):
        # self.ctrlPair.setEnabled(False)

        self.pairComboFilter = ControlComboBox()
        self.pairComboFilter.setObjectName('pairComboFilter')
        # self.pairComboFilter.addItems(['BTC', 'USD', 'ETH', 'BNB'])

        # create the main and the proxy models
        pairModel = PairComboBoxModel([])
        pairFilterModel = PairFilterProxyModel()
        pairFilterModel.setSourceModel(pairModel)
        pairFilterModel.setDynamicSortFilter(True)
        self.pairComboFilter.currentTextChanged.connect(pairFilterModel.setPairFilter)

        # create table view
        pairView = PairTableView()
        pairView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        pairView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        pairView.setSortingEnabled(True)
        pairView.setShowGrid(False)
        pairView.setMinimumWidth(500)
        new_font = pairView.font()
        new_font.setPointSize(8)
        pairView.setFont(new_font)
        # pairView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # pairView.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerItem)

        # create the header for the table view
        pairView.setHorizontalHeader(PairComboBoxHeader(self.pairComboFilter))
        pairView.horizontalHeader().setStretchLastSection(True)
        pairView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        pairView.horizontalHeader().setMinimumHeight(35)
        pairView.verticalHeader().setDefaultSectionSize(24);
        pairView.verticalHeader().setMaximumHeight(360)
        pairView.verticalHeader().hide()

        pairFilterModel.filterChanged.connect(pairView.handleFilterChanged)

        # set model and view to pairCombo
        self.ctrlPair.setView(pairView)
        self.ctrlPair.view().setRowHidden(0, True)
        self.ctrlPair.setModel(pairFilterModel)

        # set pairComboFilter into the header
        i = self.ctrlPair.model().index(0,0)
        self.ctrlPair.view().horizontalHeader().setIndexWidget(i, self.pairComboFilter)



    def setOverlayCombo(self):
        # Set overlays
        overlayList = OverlayFactory.getOverlayNames()
        self.ctrlOverlay.setView(QtWidgets.QListView())  # this is a workaround for the known Qt > 5.5 bug
        # which happens only with Fusion style
        overlayModel = self.ctrlOverlay.model()
        # set the sticky name 'Overlay' as the first item and hide it
        item = QtGui.QStandardItem('Overlays')
        item.setSelectable(False)
        overlayModel.setItem(0, item)
        self.ctrlOverlay.view().setRowHidden(0, True)
        # set actual overlay items
        for i in range(len(overlayList)):
            item = QtGui.QStandardItem(overlayList[i])
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Unchecked)
            overlayModel.setItem(i+1, item)


    def setIndicatorCombo(self):
        # Set indicators
        indicatorList = IndicatorFactory.getIndicatorNames()
        self.ctrlIndicator.setView(QtWidgets.QListView())  # this is a workaround for the known Qt > 5.5 bug
        # which happens only with Fusion style
        indicatorModel = self.ctrlIndicator.model()
        # set the sticky name 'Indicator' as the first item and hide it
        item = QtGui.QStandardItem('Indicators')
        item.setSelectable(False)
        indicatorModel.setItem(0, item)
        self.ctrlIndicator.view().setRowHidden(0, True)
        # set actual indicator items
        for i in range(len(indicatorList)):
            item = QtGui.QStandardItem(indicatorList[i])
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Unchecked)
            indicatorModel.setItem(i+1, item)

    # ------------------------------------------------------------------------------------
    # Event Handlers
    # ------------------------------------------------------------------------------------

    def exchangeChanged(self, item):
        self.parent().exchangeChanged(item)
        self.ctrlPair.setEnabled(True)

    def pairChanged(self, item):
        self.ctrlTime.setEnabled(True)
        self.parent().pairChanged(item)

    def intervalChanged(self, item):
        self.parent().intervalChanged(item)

    def overlayChanged(self, item):
        if self.itemChangedByUser:
            if item.checkState() == QtCore.Qt.Checked:
                self.parent().chartWidget.addOverlay(item.text())
            else:
                self.parent().chartWidget.removeOverlay(item.text())

    def indicatorChanged(self, item):
        if self.itemChangedByUser:
            if item.checkState() == QtCore.Qt.Checked:
                self.parent().chartWidget.showIndicator(item.text())
            else:
                self.parent().chartWidget.hideIndicator(item.text())


    # ------------------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------------------

    def setExchangeList(self, exchangeList):
        self.ctrlExchange.blockSignals(True)
        self.ctrlExchange.view().setRowHidden(0, True)
        self.ctrlExchange.addItems(exchangeList)
        self.ctrlExchange.blockSignals(False)

    def setPairList(self, tickers, quote_currencies):
        try:
            # set quote currencies to the filter combo
            self.pairComboFilter.blockSignals(True)
            self.pairComboFilter.clear()
            self.pairComboFilter.addItems(quote_currencies)
            self.pairComboFilter.blockSignals(False)

            # update pair combo model
            self.ctrlPair.blockSignals(True)
            self.ctrlPair.model().sourceModel().clear()
            pairList = []
            for symbol, data in tickers.items():
                price  = float(data[4])
                change = float(data[7])
                volume = int(price * float(data[5]))
                pairList.append( [ symbol, price, change, volume ] )
            self.ctrlPair.model().setPairFilter(quote_currencies[0])
            self.ctrlPair.model().sourceModel().setTableData(pairList)
            self.ctrlPair.view().setRowHidden(0, True)
            self.ctrlTime.setEnabled(False)
            self.ctrlPair.blockSignals(False)
        except Exception as e:
            print(e)

    def setIntervalList(self, intervalList):
        self.ctrlTime.blockSignals(True)
        self.ctrlTime.clear()
        self.ctrlTime.addItems(['TIME'] + intervalList)
        self.ctrlTime.view().setRowHidden(0, True)
        for i in range(0, self.ctrlTime.model().rowCount()):
            self.ctrlTime.model().item(i).setData(QtCore.Qt.AlignHCenter, QtCore.Qt.TextAlignmentRole)
        self.ctrlTime.blockSignals(False)


    # ------------------------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------------------------

    def loadConfiguration(self, config):
        exchange = config['EXCHANGE']['exchange']
        pair = config['EXCHANGE']['pair']
        interval = config['EXCHANGE']['interval']

        if exchange:
            self.ctrlExchange.setCurrentText(exchange)
            if pair:
                self.ctrlPair.setCurrentText(pair)
                if interval:
                    self.ctrlTime.setCurrentText(interval)

        overlays = config['TradingChart']['overlays']
        if overlays:
            overlays = overlays.split(',')
            for i in range(self.ctrlOverlay.model().rowCount()):
                item = self.ctrlOverlay.model().item(i)
                if item.text() in overlays:
                    item.setCheckState(QtCore.Qt.Checked)

        indicators = config['TradingChart']['indicators']
        if indicators:
            indicators = indicators.split(',')
            for i in range(self.ctrlIndicator.model().rowCount()):
                item = self.ctrlIndicator.model().item(i)
                if item.text() in indicators:
                    item.setCheckState(QtCore.Qt.Checked)


    def saveConfiguration(self, config):
        exchange = self.ctrlExchange.currentText() if self.ctrlExchange.currentIndex() > 0 else ''
        pair = self.ctrlPair.currentText() if self.ctrlPair.currentText() != 'PAIR' else ''
        interval = self.ctrlTime.currentText() if self.ctrlTime.currentText() != 'TIME' else ''

        overlays = []
        for i in range(self.ctrlOverlay.model().rowCount()):
            item = self.ctrlOverlay.model().item(i)
            if item.checkState() == QtCore.Qt.Checked:
                overlays.append(item.text())

        indicators = []
        for i in range(self.ctrlIndicator.model().rowCount()):
            item = self.ctrlIndicator.model().item(i)
            if item.checkState() == QtCore.Qt.Checked:
                indicators.append(item.text())

        config['EXCHANGE'] = {'exchange': exchange,
                              'pair'    : pair,
                              'interval': interval}
        config['TradingChart'] = {
            'overlays'  : ','.join(overlays),
            'indicators': ','.join(indicators)
        }