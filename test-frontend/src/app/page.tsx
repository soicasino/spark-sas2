"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Switch } from "@/components/ui/switch";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { CreditCard, DollarSign, Settings, Activity, AlertCircle, CheckCircle, Wifi, WifiOff, RefreshCcw, Power, Lock, Unlock, X } from "lucide-react";

import { sasApi, SASWebSocketClient, CardReaderStatus, MeterData, BillAcceptorStatus, EventStats } from "@/lib/api";

export default function SASDashboard() {
  // State management
  const [cardStatus, setCardStatus] = useState<CardReaderStatus | null>(null);
  const [meters, setMeters] = useState<MeterData | null>(null);
  const [billAcceptorStatus, setBillAcceptorStatus] = useState<BillAcceptorStatus | null>(null);
  const [eventStats, setEventStats] = useState<EventStats | null>(null);
  const [liveEvents, setLiveEvents] = useState<any[]>([]);
  const [systemStatus, setSystemStatus] = useState<any>(null);

  const [loading, setLoading] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);

  // Money transfer state
  const [transferAmount, setTransferAmount] = useState<string>("");
  const [transferType, setTransferType] = useState<"add" | "subtract">("add");

  // WebSocket connection
  const [wsClient] = useState(() => new SASWebSocketClient());

  // Initialize data and WebSocket connection
  useEffect(() => {
    initializeDashboard();

    // Setup WebSocket for live updates
    wsClient.connect(
      (data) => {
        console.log("WebSocket data received:", data);
        setWsConnected(true);

        // Handle different event types
        if (data.type === "card_events") {
          console.log("Card event received:", data);
          setLiveEvents((prev) => [data, ...prev.slice(0, 49)]); // Keep last 50 events
          refreshCardStatus(); // Refresh card status on card events
        } else if (data.type === "game_event") {
          setLiveEvents((prev) => [data, ...prev.slice(0, 49)]);
        } else if (data.type === "meter_update") {
          refreshMeters(); // Refresh meters on updates
        } else if (data.type === "bill_acceptor_event") {
          refreshBillAcceptorStatus();
        }

        // Add to live events
        setLiveEvents((prev) => [data, ...prev.slice(0, 49)]);
      },
      (error) => {
        console.error("WebSocket error:", error);
        setWsConnected(false);
      }
    );

    // Cleanup WebSocket on unmount
    return () => {
      wsClient.disconnect();
    };
  }, []);

  const initializeDashboard = async () => {
    await Promise.all([refreshCardStatus(), refreshMeters(), refreshBillAcceptorStatus(), refreshEventStats(), refreshSystemStatus()]);
  };

  const setLoadingState = (key: string, state: boolean) => {
    setLoading((prev) => ({ ...prev, [key]: state }));
  };

  const handleApiCall = async (key: string, apiCall: () => Promise<any>, onSuccess?: (data: any) => void) => {
    setLoadingState(key, true);
    setError(null);

    try {
      const result = await apiCall();
      if (onSuccess) onSuccess(result);
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      console.error(`API call failed for ${key}:`, err);
    } finally {
      setLoadingState(key, false);
    }
  };

  // Refresh functions
  const refreshCardStatus = () =>
    handleApiCall(
      "cardStatus",
      () => sasApi.getCardReaderStatus(),
      (data) => {
        console.log("Card status refreshed:", data);
        setCardStatus(data);
      }
    );

  const refreshMeters = () => handleApiCall("meters", () => sasApi.getAllMeters(), setMeters);

  const refreshBillAcceptorStatus = () => handleApiCall("billAcceptor", () => sasApi.getBillAcceptorStatus(), setBillAcceptorStatus);

  const refreshEventStats = () => handleApiCall("eventStats", () => sasApi.getEventStats(), setEventStats);

  const refreshSystemStatus = () => handleApiCall("systemStatus", () => sasApi.getSystemStatus(), setSystemStatus);

  // Card Reader Actions
  const handleEjectCard = () =>
    handleApiCall(
      "ejectCard",
      () => sasApi.ejectCard(),
      () => {
        setTimeout(refreshCardStatus, 1000); // Refresh after a delay
      }
    );

  // Bill Acceptor Actions
  const handleToggleBillAcceptor = (enabled: boolean) => {
    const action = enabled ? sasApi.enableBillAcceptor() : sasApi.disableBillAcceptor();
    handleApiCall(
      "toggleBillAcceptor",
      () => action,
      () => {
        setTimeout(refreshBillAcceptorStatus, 500);
      }
    );
  };

  // Money Transfer Actions
  const handleMoneyTransfer = () => {
    const amount = parseFloat(transferAmount);
    if (isNaN(amount) || amount <= 0) {
      setError("Please enter a valid amount");
      return;
    }

    const action = transferType === "add" ? "add_credits" : "subtract_credits";

    handleApiCall(
      "moneyTransfer",
      () => sasApi.controlMachine(action, amount),
      () => {
        setTransferAmount("");
        setTimeout(refreshMeters, 500); // Refresh meters to see balance changes
      }
    );
  };

  // Machine Control Actions
  const handleLockMachine = () => handleApiCall("lockMachine", () => sasApi.lockMachine());
  const handleUnlockMachine = () => handleApiCall("unlockMachine", () => sasApi.unlockMachine());
  const handleEmergencyStop = () => handleApiCall("emergencyStop", () => sasApi.emergencyStop());

  // Event Management Actions
  const handleForceSync = () => handleApiCall("forceSync", () => sasApi.forceSync(), refreshEventStats);
  const handleTestGameEvent = () => handleApiCall("testGameEvent", () => sasApi.testGameEvent());
  const handleTestCardEvent = () => handleApiCall("testCardEvent", () => sasApi.testCardEvent());

  const formatCurrency = (amount: number) => `$${amount.toFixed(2)}`;
  const formatTimestamp = (timestamp: string) => new Date(timestamp).toLocaleTimeString();

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">SAS Slot Machine Dashboard</h1>
            <p className="text-muted-foreground">Real-time monitoring and control</p>
          </div>

          <div className="flex items-center space-x-4">
            <Badge variant={wsConnected ? "default" : "secondary"} className="flex items-center gap-2">
              {wsConnected ? <Wifi className="h-4 w-4" /> : <WifiOff className="h-4 w-4" />}
              {wsConnected ? "Live Connected" : "Disconnected"}
            </Badge>

            <Button onClick={initializeDashboard} variant="outline" size="sm">
              <RefreshCcw className="h-4 w-4 mr-2" />
              Refresh All
            </Button>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
            <Button variant="ghost" size="sm" onClick={() => setError(null)} className="ml-auto">
              <X className="h-4 w-4" />
            </Button>
          </Alert>
        )}

        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="card-reader">Card Reader</TabsTrigger>
            <TabsTrigger value="meters">Meters</TabsTrigger>
            <TabsTrigger value="bill-acceptor">Bill Acceptor</TabsTrigger>
            <TabsTrigger value="events">Live Events</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Card Status Overview */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Card Reader</CardTitle>
                  <CreditCard className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{cardStatus?.card_inserted ? "Card Present" : "No Card"}</div>
                  <p className="text-xs text-muted-foreground">{cardStatus?.card_number || "No card detected"}</p>
                  <p className="text-xs text-gray-500">Debug: {JSON.stringify(cardStatus)}</p>
                </CardContent>
              </Card>

              {/* Balance Overview */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Current Balance</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {meters?.data.meters?.current_credits ? formatCurrency(meters.data.meters.current_credits / 100) : "$0.00"}
                  </div>
                  <p className="text-xs text-muted-foreground">Credits: {meters?.data.meters?.current_credits || 0}</p>
                </CardContent>
              </Card>

              {/* Bill Acceptor Overview */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Bill Acceptor</CardTitle>
                  <Settings className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{billAcceptorStatus?.data.enabled ? "Enabled" : "Disabled"}</div>
                  <p className="text-xs text-muted-foreground">
                    Available: {billAcceptorStatus?.data.available ? "Yes" : "No"} | Pooling: {billAcceptorStatus?.data.pooling_started ? "Started" : "Stopped"}
                  </p>
                </CardContent>
              </Card>

              {/* Events Overview */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Event Sync</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{eventStats?.data.is_online ? "Online" : "Offline"}</div>
                  <p className="text-xs text-muted-foreground">Unsynced: {eventStats?.data.unsynced_events.total || 0}</p>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Common machine operations</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Button variant="outline" onClick={handleLockMachine} disabled={loading.lockMachine} className="flex items-center gap-2">
                  <Lock className="h-4 w-4" />
                  Lock Machine
                </Button>

                <Button variant="outline" onClick={handleUnlockMachine} disabled={loading.unlockMachine} className="flex items-center gap-2">
                  <Unlock className="h-4 w-4" />
                  Unlock Machine
                </Button>

                <Button variant="destructive" onClick={handleEmergencyStop} disabled={loading.emergencyStop} className="flex items-center gap-2">
                  <Power className="h-4 w-4" />
                  Emergency Stop
                </Button>

                <Button variant="outline" onClick={handleForceSync} disabled={loading.forceSync} className="flex items-center gap-2">
                  <RefreshCcw className="h-4 w-4" />
                  Force Sync
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Card Reader Tab */}
          <TabsContent value="card-reader" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CreditCard className="h-5 w-5" />
                    Card Reader Status
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Status:</span>
                    <Badge variant={cardStatus?.card_inserted ? "default" : "secondary"}>{cardStatus?.formatted_display?.card_status || "Unknown"}</Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <span>Card Present:</span>
                    <Badge variant={cardStatus?.card_inserted ? "default" : "outline"}>{cardStatus?.card_inserted ? "Yes" : "No"}</Badge>
                  </div>

                  <div className="text-xs text-gray-500 mt-2">Debug: {JSON.stringify(cardStatus, null, 2)}</div>

                  {cardStatus?.card_number && (
                    <div className="flex items-center justify-between">
                      <span>Card Number:</span>
                      <code className="text-sm bg-muted px-2 py-1 rounded">{cardStatus.card_number}</code>
                    </div>
                  )}

                  <div className="flex items-center justify-between">
                    <span>Last Updated:</span>
                    <span className="text-sm text-muted-foreground">{cardStatus?.timestamp ? formatTimestamp(cardStatus.timestamp) : "Never"}</span>
                  </div>

                  <Separator />

                  <div className="flex gap-2">
                    <Button onClick={refreshCardStatus} disabled={loading.cardStatus} variant="outline" className="flex-1">
                      {loading.cardStatus ? <RefreshCcw className="h-4 w-4 animate-spin" /> : "Refresh"}
                    </Button>

                    <Button onClick={handleEjectCard} disabled={loading.ejectCard || !cardStatus?.card_inserted} variant="destructive" className="flex-1">
                      Eject Card
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Test Card Events</CardTitle>
                  <CardDescription>Generate test events for debugging</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Button onClick={handleTestCardEvent} disabled={loading.testCardEvent} variant="outline" className="w-full">
                    Test Card Insert Event
                  </Button>

                  <Button
                    onClick={() => handleApiCall("testCardRemove", () => sasApi.testCardEvent("card_removed"))}
                    disabled={loading.testCardRemove}
                    variant="outline"
                    className="w-full">
                    Test Card Remove Event
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Meters Tab */}
          <TabsContent value="meters" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <DollarSign className="h-5 w-5" />
                    Current Meters
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {meters?.data.meters ? (
                    <div className="space-y-3">
                      {Object.entries(meters.data.meters).map(([key, value]) => (
                        <div key={key} className="flex items-center justify-between">
                          <span className="capitalize">{key.replace(/_/g, " ")}:</span>
                          <span className="font-mono">{typeof value === "number" && key.includes("credit") ? formatCurrency(value / 100) : String(value)}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-muted-foreground">No meter data available</p>
                  )}

                  <Separator className="my-4" />

                  <div className="grid grid-cols-2 gap-2">
                    <Button onClick={refreshMeters} disabled={loading.meters} variant="outline">
                      {loading.meters ? <RefreshCcw className="h-4 w-4 animate-spin" /> : "Refresh"}
                    </Button>

                    <Button
                      onClick={() => handleApiCall("requestMeters", () => sasApi.requestMeters("all"))}
                      disabled={loading.requestMeters}
                      variant="outline">
                      Request Update
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Money Transfer</CardTitle>
                  <CardDescription>Add or subtract credits from the machine</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="transfer-amount">Amount ($)</Label>
                    <Input
                      id="transfer-amount"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={transferAmount}
                      onChange={(e) => setTransferAmount(e.target.value)}
                    />
                  </div>

                  <div className="flex items-center space-x-2">
                    <Label htmlFor="transfer-type">Transfer Type:</Label>
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        <input type="radio" id="add-credits" name="transfer-type" checked={transferType === "add"} onChange={() => setTransferType("add")} />
                        <Label htmlFor="add-credits">Add Credits</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <input
                          type="radio"
                          id="subtract-credits"
                          name="transfer-type"
                          checked={transferType === "subtract"}
                          onChange={() => setTransferType("subtract")}
                        />
                        <Label htmlFor="subtract-credits">Subtract Credits</Label>
                      </div>
                    </div>
                  </div>

                  <Button
                    onClick={handleMoneyTransfer}
                    disabled={loading.moneyTransfer || !transferAmount}
                    className="w-full"
                    variant={transferType === "add" ? "default" : "destructive"}>
                    {transferType === "add" ? "Add" : "Subtract"} Credits
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Bill Acceptor Tab */}
          <TabsContent value="bill-acceptor" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="h-5 w-5" />
                    Bill Acceptor Control
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Status:</span>
                    <Badge variant={billAcceptorStatus?.data.enabled ? "default" : "secondary"}>
                      {billAcceptorStatus?.data.available ? (billAcceptorStatus.data.enabled ? "Enabled" : "Disabled") : "Not Available"}
                    </Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <Label htmlFor="bill-acceptor-toggle">Enable Bill Acceptor:</Label>
                    <Switch
                      id="bill-acceptor-toggle"
                      checked={billAcceptorStatus?.data.enabled || false}
                      onCheckedChange={handleToggleBillAcceptor}
                      disabled={loading.toggleBillAcceptor}
                    />
                  </div>

                  {billAcceptorStatus?.data.last_bill_amount && (
                    <div className="flex items-center justify-between">
                      <span>Last Bill:</span>
                      <span className="font-mono">{formatCurrency(billAcceptorStatus.data.last_bill_amount)}</span>
                    </div>
                  )}

                  {billAcceptorStatus?.data.total_inserted && (
                    <div className="flex items-center justify-between">
                      <span>Total Inserted:</span>
                      <span className="font-mono">{formatCurrency(billAcceptorStatus.data.total_inserted)}</span>
                    </div>
                  )}

                  <div className="flex items-center justify-between">
                    <span>Available:</span>
                    <Badge variant={billAcceptorStatus?.data.available ? "default" : "secondary"}>{billAcceptorStatus?.data.available ? "Yes" : "No"}</Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <span>Pooling Status:</span>
                    <Badge variant={billAcceptorStatus?.data.pooling_started ? "default" : "secondary"}>
                      {billAcceptorStatus?.data.pooling_started ? "Started" : "Stopped"}
                    </Badge>
                  </div>

                  {billAcceptorStatus?.data.last_command_time && (
                    <div className="flex items-center justify-between">
                      <span>Last Command:</span>
                      <span className="text-sm text-muted-foreground">{formatTimestamp(billAcceptorStatus.data.last_command_time)}</span>
                    </div>
                  )}

                  {billAcceptorStatus?.data.type_id && (
                    <div className="flex items-center justify-between">
                      <span>Type ID:</span>
                      <span className="font-mono">{billAcceptorStatus.data.type_id}</span>
                    </div>
                  )}

                  <Separator />

                  <div className="grid grid-cols-2 gap-2">
                    <Button onClick={refreshBillAcceptorStatus} disabled={loading.billAcceptor} variant="outline">
                      {loading.billAcceptor ? <RefreshCcw className="h-4 w-4 animate-spin" /> : "Refresh"}
                    </Button>

                    <Button
                      onClick={() => handleApiCall("resetBillAcceptor", () => sasApi.resetBillAcceptor())}
                      disabled={loading.resetBillAcceptor}
                      variant="destructive">
                      Reset
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Bill Acceptor Actions</CardTitle>
                  <CardDescription>Manual control and testing</CardDescription>
                </CardHeader>
                <CardContent className="space-y-2">
                  {["start", "stop", "stack", "return"].map((action) => (
                    <Button
                      key={action}
                      onClick={() => handleApiCall(`billAction${action}`, () => sasApi.controlBillAcceptor(action))}
                      disabled={loading[`billAction${action}`]}
                      variant="outline"
                      className="w-full capitalize">
                      {action} Bill Acceptor
                    </Button>
                  ))}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Live Events Tab */}
          <TabsContent value="events" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    Live Events Feed
                  </CardTitle>
                  <CardDescription>Real-time events from WebSocket connection</CardDescription>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-96">
                    {liveEvents.length === 0 ? (
                      <p className="text-muted-foreground text-center py-8">No events received yet. Events will appear here in real-time.</p>
                    ) : (
                      <div className="space-y-2">
                        {liveEvents.map((event, index) => (
                          <div key={index} className="p-3 border rounded-lg bg-muted/50">
                            <div className="flex items-center justify-between mb-2">
                              <Badge variant="outline">{event.type || "event"}</Badge>
                              <span className="text-xs text-muted-foreground">{event.timestamp ? formatTimestamp(event.timestamp) : "Now"}</span>
                            </div>
                            <pre className="text-xs overflow-x-auto">{JSON.stringify(event, null, 2)}</pre>
                          </div>
                        ))}
                      </div>
                    )}
                  </ScrollArea>

                  <Separator className="my-4" />

                  <div className="flex gap-2">
                    <Button onClick={() => setLiveEvents([])} variant="outline" size="sm">
                      Clear Events
                    </Button>

                    <Button onClick={handleTestGameEvent} disabled={loading.testGameEvent} variant="outline" size="sm">
                      Test Game Event
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Event Statistics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Connection Status:</span>
                    <Badge variant={eventStats?.data.is_online ? "default" : "destructive"}>{eventStats?.data.is_online ? "Online" : "Offline"}</Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <span>WebSocket:</span>
                    <Badge variant={wsConnected ? "default" : "secondary"}>{wsConnected ? "Connected" : "Disconnected"}</Badge>
                  </div>

                  {eventStats?.data.unsynced_events && (
                    <>
                      <Separator />
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span>Game Events:</span>
                          <span>{eventStats.data.unsynced_events.game}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Card Events:</span>
                          <span>{eventStats.data.unsynced_events.card}</span>
                        </div>
                        <div className="flex items-center justify-between font-semibold">
                          <span>Total Unsynced:</span>
                          <span>{eventStats.data.unsynced_events.total}</span>
                        </div>
                      </div>
                    </>
                  )}

                  <Separator />

                  <div className="space-y-2">
                    <Button onClick={refreshEventStats} disabled={loading.eventStats} variant="outline" size="sm" className="w-full">
                      {loading.eventStats ? <RefreshCcw className="h-4 w-4 animate-spin" /> : "Refresh Stats"}
                    </Button>

                    <Button onClick={handleForceSync} disabled={loading.forceSync} variant="outline" size="sm" className="w-full">
                      Force Sync
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
