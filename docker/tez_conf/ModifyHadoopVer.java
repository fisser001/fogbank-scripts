import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.regex.Pattern;
import java.util.regex.Matcher;

public class ModifyHadoopVer{

    public static void main(String[] args){
        String filename = args[0];
        String hadoopVer = System.getenv("HADOOP_VER");
        Pattern p = Pattern.compile("<hadoop.version>(.+?)</hadoop.version>");

        try{
            String fileContents = "";
            BufferedReader reader = new BufferedReader(new FileReader(filename));
            for(String line=reader.readLine(); line != null; line=reader.readLine()){
                Matcher m = p.matcher(line);
                if (m.find()){
                    String version = m.group(1);
                    int start = line.indexOf(version);
                    int end = start + version.length();
                    fileContents += line.substring(0, start) + hadoopVer + line.substring(end);
                             
                } else{
                    fileContents += line;
                }
                fileContents += System.lineSeparator();
            }
            reader.close();
            FileWriter writer = new FileWriter(filename);
            writer.write(fileContents);
            writer.close();

        } catch (IOException e){
            e.printStackTrace();
        }
        
    }
}
