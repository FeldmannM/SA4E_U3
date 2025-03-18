@echo off
rem Michael Feldmann
rem Schritt 1: Kafka-Container starten (falls noch nicht gestartet)
echo Starte Kafka-Container...
docker-compose up -d

rem Kurze Wartezeit, damit die Container hochgefahren sind
echo Warte, bis die Container hochgefahren sind...
timeout /t 5 >nul

rem Schritt 2: Cluster-ID generieren
echo Generiere Cluster-ID...
for /f "delims=" %%i in ('docker exec kafka1 kafka-storage.sh random-uuid') do set CLUSTER_ID=%%i
echo Cluster-ID generiert: %CLUSTER_ID%

rem Schritt 3: Datenverzeichnisse löschen, um alte Cluster-ID zu entfernen
echo Lösche Datenverzeichnisse für kafka1...
docker exec kafka1 rm -rf /bitnami/kafka/data/*
echo Lösche Datenverzeichnisse für kafka2...
docker exec kafka2 rm -rf /bitnami/kafka/data/*
echo Lösche Datenverzeichnisse für kafka3...
docker exec kafka3 rm -rf /bitnami/kafka/data/*

rem Schritt 4: Speicher für alle Broker formatieren
echo Formatiere Speicher für kafka1...
docker exec kafka1 kafka-storage.sh format --ignore-formatted --cluster-id %CLUSTER_ID% --config /opt/bitnami/kafka/config/kraft/server.properties

echo Formatiere Speicher für kafka2...
docker exec kafka2 kafka-storage.sh format --ignore-formatted --cluster-id %CLUSTER_ID% --config /opt/bitnami/kafka/config/kraft/server.properties

echo Formatiere Speicher für kafka3...
docker exec kafka3 kafka-storage.sh format --ignore-formatted --cluster-id %CLUSTER_ID% --config /opt/bitnami/kafka/config/kraft/server.properties

rem Schritt 5: Container neu starten, damit die Formatierung wirksam wird
rem echo Starte Kafka-Container neu, um formatierten Speicher zu laden...
rem docker restart kafka1 kafka2 kafka3

echo Alle Broker erfolgreich formatiert und mit Cluster-ID %CLUSTER_ID% gestartet.
pause
