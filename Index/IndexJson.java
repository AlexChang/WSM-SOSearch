import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.*;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.FieldInfo;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.Term;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TermQuery;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.JSONValue;

import java.io.*;
import java.nio.file.Paths;
import java.util.List;
import java.util.Set;

public class IndexJson {

    static final String INDEX_PATH = "C:/Users/dry99/Desktop/lucenetest/index";
    static final String JSON_FILE_PATH = "C:/Users/dry99/Desktop/lucenetest/files/doc.json";
  

    String indexPath;
    String jsonFilePath;
    IndexWriter indexWriter = null;

    public IndexJson(String indexPath, String jsonFilePath) {
        this.indexPath = indexPath;
        this.jsonFilePath = jsonFilePath;
    }

    public void createIndex() throws FileNotFoundException {
        JSONArray jsonObjects = parseJSONFile();
        openIndex();
        addDocuments(jsonObjects);
        finish();
    }

    public JSONArray parseJSONFile() throws FileNotFoundException {
        InputStream jsonFile = new FileInputStream(jsonFilePath);
        Reader readerJson = new InputStreamReader(jsonFile);
        //Parse the json file using simple-json library
        Object fileObjects = JSONValue.parse(readerJson);
        JSONArray arrayObjects = (JSONArray) fileObjects;
        return arrayObjects;
    }

    public boolean openIndex() {
        try {
            //InputStream stopWords = new FileInputStream(STOPWORDS_FILE_PATH);
            //Reader readerStopWords = new InputStreamReader(stopWords);
            Directory dir = FSDirectory.open(Paths.get(INDEX_PATH));
            StandardAnalyzer analyzer = new StandardAnalyzer();
            IndexWriterConfig iwc = new IndexWriterConfig(analyzer);
            iwc.setOpenMode(IndexWriterConfig.OpenMode.CREATE);
            indexWriter = new IndexWriter(dir, iwc);
            return true;
        } catch (Exception e) {
            System.err.println("Error opening the index. " + e.getMessage());
        }
        return false;
    }

    /**
     * Add documents to the index
     */
    public void addDocuments(JSONArray jsonObjects){
    	int index_a = 0;
    	int index_q = 0;
        for(JSONObject object : (List<JSONObject>) jsonObjects)
        {
            Document doc = new Document();
            for(String field : (Set<String>) object.keySet())
            {
            	//System.out.println(field);
            	if(field.equals("answers"))
            	{
            		index_a += 1;
            		System.out.println("answers" + index_a);
            		JSONArray  fieldContent =   (JSONArray) object.get("answers");
            		//System.out.println(fieldContent );
            		for (Object elem : fieldContent) 
            		{
            			try
            			{
            				//System.out.println(elem );
                			//System.out.println(((JSONObject) elem).keySet());
                			if(((JSONObject) elem).keySet().contains("comments"))
                			{
                				String comments = (((JSONObject) elem).get("comments")).toString();
                				doc.add(new TextField("comments", comments,Field.Store.YES));
                			}
                			if(((JSONObject) elem).keySet().contains("accepted"))
                			{
                				String accepted = (((JSONObject) elem).get("accepted")).toString();
                				doc.add(new TextField("accepted", accepted,Field.Store.YES));
                			}
                			if(((JSONObject) elem).keySet().contains("vote"))
                			{
                				String vote = (((JSONObject) elem).get("vote")).toString();
                				doc.add(new TextField("vote", vote,Field.Store.YES));
                			}
                			if(((JSONObject) elem).keySet().contains("content"))
                			{
                				String content = (((JSONObject) elem).get("content")).toString();
                				doc.add(new TextField("content", content,Field.Store.YES));
                			}	
                			if(((JSONObject) elem).keySet().contains("users"))
                			{
                				String users = (((JSONObject) elem).get("users")).toString();
                				doc.add(new TextField("users", users,Field.Store.YES));
                			}	
            			}
            			catch(Exception e){
                            System.err.println("Error adding documents to the index in " + elem);
                        }
            		}
            	}
            	if(field.equals("question"))
            	{
            		index_q += 1;
            		System.out.println("question" + index_q);
            		JSONObject  fieldContent =   (JSONObject) object.get("question");
            		//System.out.println(fieldContent.keySet());
            		//System.out.println(fieldContent );
            		try
            		{
            			if(fieldContent.keySet().contains("tag"))
            			{
            				String tag = (((JSONObject) fieldContent).get("tag")).toString();
            				doc.add(new TextField("tag", tag,Field.Store.YES));
            			}
            			if(fieldContent.keySet().contains("content"))
            			{
            				String content = (((JSONObject) fieldContent).get("content")).toString();
            				doc.add(new TextField("content", content,Field.Store.YES));
            			}
            			if(fieldContent.keySet().contains("user"))
            			{
            				String user = (((JSONObject) fieldContent).get("user")).toString();
            				doc.add(new TextField("user", user,Field.Store.YES));
            			}
            			if(fieldContent.keySet().contains("comments"))
            			{
            				String comments = (((JSONObject) fieldContent).get("comments")).toString();
            				doc.add(new TextField("comments", comments,Field.Store.YES));
            			}	
            			if(fieldContent.keySet().contains("link"))
            			{
            				String link = (((JSONObject) fieldContent).get("link")).toString();
            				doc.add(new TextField("link", link,Field.Store.YES));
            				//System.out.println(link);
            			}
            			if(fieldContent.keySet().contains("title"))
            			{
            				String title = (((JSONObject) fieldContent).get("title")).toString();
            				doc.add(new TextField("title", title,Field.Store.YES));
            			}
            			if(fieldContent.keySet().contains("vote"))
            			{
            				String vote = (((JSONObject) fieldContent).get("vote")).toString();
            				doc.add(new TextField("vote", vote,Field.Store.YES));
            			}
            		}
            		catch(Exception e){
                        System.err.println("Error adding documents to the index in " + fieldContent);
                    }
            		
        		}
            }
            try {
            	//fieldContent.keySet()
                indexWriter.addDocument(doc);
            } catch (IOException ex) {
                System.err.println("Error adding documents to the index. " +  ex.getMessage());
            }
        }
        System.out.println("Finish Indexing");
    }

    /**
     * Write the document to the index and close it
     */
    public void finish() {
        try {
            indexWriter.commit();
            indexWriter.close();
        } catch (IOException ex) {
            System.err.println("We had a problem closing the index: " + ex.getMessage());
        }
    }
    
     public static String testQueryLucene() throws IOException {
    	String res = "";
        Directory indexDirectory = FSDirectory.open(Paths.get(INDEX_PATH));
        IndexReader indexReader = DirectoryReader.open(indexDirectory);
        final IndexSearcher indexSearcher = new IndexSearcher(indexReader);
        Term t = new Term("content","app");
        Query query = new TermQuery(t);
        TopDocs topDocs = indexSearcher.search(query, 10);
        
        ScoreDoc[] sds = topDocs.scoreDocs;
   
	    int cou=0;
	    System.out.println(sds.length);
	    for(ScoreDoc sd:sds)
	    {
	       cou++;
	       Document d = indexSearcher.doc(sd.doc);
	       //System.out.println(sds);
	       res+=cou+". "+d.get("link")+"\n";
	    }
	    return res;
    }
    

    

    public static void main(String[] args) throws IOException {
    	IndexJson liw = new IndexJson(INDEX_PATH, JSON_FILE_PATH);
        liw.createIndex();
        System.out.println(liw.testQueryLucene());
    }

}
