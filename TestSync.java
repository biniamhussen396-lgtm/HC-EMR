import et.edu.uog.AvailabilitySender;

public class TestSync {
    public static void main(String[] args) {
        String state = args.length > 0 ? args[0] : "active";
        boolean res = AvailabilitySender.send("6092AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", state);
        System.out.println("Result: " + res);
    }
}
