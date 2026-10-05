import java.nio.file.Path;
import com.google.inject.Injector;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.xtext.diagnostics.Severity;
import org.eclipse.xtext.util.CancelIndicator;
import org.eclipse.xtext.validation.CheckMode;
import org.eclipse.xtext.validation.IResourceValidator;
import org.omg.kerml.xtext.KerMLStandaloneSetup;
import org.omg.sysml.io.SysMLUtil;
import org.omg.sysml.util.SysMLLibraryUtil;
import org.omg.sysml.xtext.SysMLStandaloneSetup;

/** Small local harness around the unmodified official Pilot validator. */
public class ValidateSysML extends SysMLUtil {
    public ValidateSysML() {
        addExtension(".kerml");
        addExtension(".sysml");
        setVerbose(false);
    }
    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            System.err.println("Usage: ValidateSysML <library-dir> <model.sysml>");
            System.exit(2);
        }
        KerMLStandaloneSetup.doSetup();
        Injector injector = new SysMLStandaloneSetup().createInjectorAndDoEMFRegistration();
        ValidateSysML loader = new ValidateSysML();
        String library = Path.of(args[0]).toAbsolutePath().toString();
        SysMLLibraryUtil.setModelLibraryDirectory(library + "/");
        loader.readAll(library + "/Kernel Libraries", false);
        loader.readAll(library + "/Systems Library", false);
        loader.readAll(library + "/Domain Libraries", false);
        System.out.println("Loaded library resources: " + loader.getResourceSet().getResources().size());
        Resource model = loader.readResource(Path.of(args[1]).toAbsolutePath().toString());
        loader.addInputResource(model);
        var issues = injector.getInstance(IResourceValidator.class)
            .validate(model, CheckMode.ALL, CancelIndicator.NullImpl);
        long errors = 0;
        for (var issue : issues) {
            System.out.printf("%s line %s: %s%n", issue.getSeverity(), issue.getLineNumber(), issue.getMessage());
            if (issue.getSeverity() == Severity.ERROR) errors++;
        }
        System.out.printf("Validation complete: %d errors, %d total diagnostics.%n", errors, issues.size());
        System.exit(errors == 0 ? 0 : 1);
    }
}
