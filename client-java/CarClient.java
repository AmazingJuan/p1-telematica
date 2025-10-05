import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.net.*;
import org.json.JSONObject;

public class CarClient extends JFrame {
    private JTextArea telemetryArea;
    private JTextField inputField, hostField, portField, passwordField;
    private JButton connectButton, sendButton, disconnectButton;
    private Socket socket;
    private BufferedReader in;
    private PrintWriter out;
    private Thread readerThread;
    private boolean isAdmin = false;

    public CarClient() {
        setTitle("Cliente Telemetría - Java Swing");
        setSize(500, 450);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout(10, 10));

        // ----- PANEL SUPERIOR: conexión -----
        JPanel topPanel = new JPanel(new GridLayout(3, 2, 5, 5));
        topPanel.add(new JLabel("Host:"));
        hostField = new JTextField("localhost");
        topPanel.add(hostField);

        topPanel.add(new JLabel("Puerto:"));
        portField = new JTextField("5000");
        topPanel.add(portField);

        topPanel.add(new JLabel("Contraseña (solo admin):"));
        passwordField = new JTextField();
        topPanel.add(passwordField);

        add(topPanel, BorderLayout.NORTH);

        // ----- PANEL CENTRAL: telemetría -----
        telemetryArea = new JTextArea();
        telemetryArea.setEditable(false);
        add(new JScrollPane(telemetryArea), BorderLayout.CENTER);

        // ----- PANEL INFERIOR: entrada y botones -----
        JPanel bottomPanel = new JPanel(new BorderLayout(5, 5));
        inputField = new JTextField();
        sendButton = new JButton("Enviar comando");
        connectButton = new JButton("Conectar");
        disconnectButton = new JButton("Desconectar");

        JPanel buttonPanel = new JPanel();
        buttonPanel.add(connectButton);
        buttonPanel.add(sendButton);
        buttonPanel.add(disconnectButton);
        bottomPanel.add(inputField, BorderLayout.CENTER);
        bottomPanel.add(buttonPanel, BorderLayout.SOUTH);
        add(bottomPanel, BorderLayout.SOUTH);

        // Estado inicial
        sendButton.setEnabled(false);
        disconnectButton.setEnabled(false);

        // ----- ACCIONES -----
        connectButton.addActionListener(e -> connectToServer());
        sendButton.addActionListener(e -> sendCommand());
        disconnectButton.addActionListener(e -> disconnect());

        inputField.addActionListener(e -> sendCommand());
    }

    private void connectToServer() {
        String host = hostField.getText().trim();
        int port = Integer.parseInt(portField.getText().trim());
        String password = passwordField.getText().trim();

        try {
            socket = new Socket(host, port);
            in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            out = new PrintWriter(socket.getOutputStream(), true);

            telemetryArea.append("Conectado al servidor\n");

            // Hilo para recibir datos continuamente
            readerThread = new Thread(() -> {
                try {
                    String line;
                    while ((line = in.readLine()) != null) {
                        if (line.contains("You are observer")) {
                            telemetryArea.append("Modo: OBSERVADOR\n");
                            if (!password.isEmpty()) {
                                out.println("AUTH " + password);
                            }
                        } else if (line.contains("Welcome ADMIN")) {
                            isAdmin = true;
                            SwingUtilities.invokeLater(() -> sendButton.setEnabled(true));
                            telemetryArea.append("Modo: ADMIN\n");
                        } else if (line.startsWith("{")) {
                            JSONObject json = new JSONObject(line);
                            SwingUtilities.invokeLater(() -> telemetryArea.setText(
                                "📊 TELEMETRÍA\n" +
                                "Velocidad: " + json.getDouble("speed") + " km/h\n" +
                                "Batería: " + json.getDouble("battery") + "%\n" +
                                "Temperatura: " + json.getDouble("temperature") + " °C\n" +
                                "Dirección: " + json.getString("direction") + "\n"
                            ));
                        } else {
                            telemetryArea.append(line + "\n");
                        }
                    }
                } catch (Exception ex) {
                    telemetryArea.append("Desconectado del servidor.\n");
                }
            });
            readerThread.start();

            connectButton.setEnabled(false);
            disconnectButton.setEnabled(true);
            if (!isAdmin) sendButton.setEnabled(false); // observador sin comandos

        } catch (Exception ex) {
            telemetryArea.append("Error: " + ex.getMessage() + "\n");
        }
    }

    private void sendCommand() {
        if (socket == null || socket.isClosed()) return;
        String cmd = inputField.getText().trim();
        if (!cmd.isEmpty()) {
            out.println(cmd);
            inputField.setText("");
        }
    }

    private void disconnect() {
        try {
            if (socket != null && !socket.isClosed()) {
                out.close();
                in.close();
                socket.close();
                telemetryArea.append("Desconectado del servidor.\n");
            }
        } catch (IOException ignored) {}

        // Restaurar estado de botones
        connectButton.setEnabled(true);
        sendButton.setEnabled(false);
        disconnectButton.setEnabled(false);
        isAdmin = false;
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new CarClient().setVisible(true));
    }
}
