import java.io.*;
import java.net.*;
import java.util.Scanner;

public class Client {
    public static void main(String[] args) {
        String host = "localhost";
        int port = 5000;

        try (Socket socket = new Socket(host, port);
             BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
             PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
             Scanner scanner = new Scanner(System.in)) {

            // Hilo para escuchar mensajes del servidor
            Thread listener = new Thread(() -> {
                try {
                    String response;
                    while ((response = in.readLine()) != null) {
                        System.out.println("SERVER: " + response);
                    }
                } catch (IOException e) {
                    System.out.println("Conexión cerrada.");
                }
            });
            listener.start();

            System.out.println("Conectado al servidor. Escribe comandos:");
            System.out.println("Ejemplo: AUTH admin123, SPEED UP, TURN LEFT, LIST USERS...");

            // Enviar comandos desde la consola
            while (true) {
                String cmd = scanner.nextLine();
                out.println(cmd);
                if (cmd.equalsIgnoreCase("EXIT")) {
                    break;
                }
            }

        } catch (IOException e) {
            System.err.println("Error de conexión: " + e.getMessage());
        }
    }
}
