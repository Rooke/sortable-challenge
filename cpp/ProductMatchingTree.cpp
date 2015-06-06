#include <jsoncpp/json/json.h>
#include <jsoncpp/json/reader.h>
#include <jsoncpp/json/writer.h>
#include <boost/algorithm/string.hpp>
#include <boost/range/algorithm/remove_if.hpp>

#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <vector>

using namespace std;

namespace ProductMatchingTree {

    typedef Json::Value Product;
    
    struct ProductNode {
        std::map<std::string, ProductNode> children;
        std::map<std::string, std::shared_ptr<Product>> products;
    };

    ostream& operator<<(std::ostream &stream, const ProductNode &product_tree){
        
        for(const auto &child : product_tree.children) {
            stream << child.second;
        }
        for(const auto &leaf : product_tree.products) {
            Json::FastWriter writer; // remove to default to 'human-readable' json
            const auto &product = leaf.second;
            stream << writer.write(*product);
        }
    }

    void search_for_product(const ProductNode &product_tree,
                            const vector<string> &tokens,
                            vector<shared_ptr<Product>> &matches){
        
        auto leaves = product_tree.products;
        auto children = product_tree.children;
    
        for(size_t i = 0; i < tokens.size(); i++){
        
            auto leaf = leaves.find(tokens[i]);
            auto child = children.find(tokens[i]);
            
            if( i != tokens.size()-1 ) {
                // Try two adjacent tokens when possible 
                string cat_token = tokens[i] + tokens[i+1];
                if(leaf == leaves.end()){
                    leaf = leaves.find(cat_token);
                }
                if(child == children.end()){
                    child = children.find(cat_token);
                }
            }
            
            if(leaf != leaves.end()){
                matches.push_back(leaf->second);
            }
            if(child != children.end()){
                search_for_product(child->second, tokens, matches);
            }
        }
    }

    const static string dubious_delimiters = "._-, ";
    const static string junk_characters = "[]/+;®";
    
    void match_listings(ofstream &results_file,
                        ifstream &listings_file,
                        ifstream &products_file){
    
        Json::Value product_json;   
        Json::Value listing_json;   
        Json::Reader reader;
    
        ProductNode product_tree;
    
        for (string line; getline(products_file, line); ){
        
            if(!reader.parse(line, product_json, false)){
                cerr << "JSON Parse error: " << endl
                     << reader.getFormatedErrorMessages();
                // Try to continue with the file
                continue;
            }
        
            string manu = product_json.get("manufacturer", "").asString();
            transform(manu.begin(), manu.end(), manu.begin(), ::toupper);
        
            string model = product_json.get("model", "").asString();
            model.erase(boost::remove_if(model, boost::is_any_of(dubious_delimiters)), model.end());
            transform(model.begin(), model.end(), model.begin(), ::toupper);


            // Construct a shallow, two-level tree
            ProductNode &product_child = product_tree.children[manu];
            product_child.products[model] = shared_ptr<Product>(new Product());
            (*product_child.products[model])["product"] = product_json;

        }

        for (string line; getline(listings_file, line); ){

            if(!reader.parse(line, listing_json, false)){
                cerr << "JSON Parse error: " << endl
                     << reader.getFormatedErrorMessages();
                // Try to continue with the file
                continue;
            }

            string title = listing_json.get("title", "" ).asString();

            title.erase(boost::remove_if(title, boost::is_any_of(junk_characters)), title.end());
            transform(title.begin(), title.end(), title.begin(), ::toupper);

            vector<string> title_tokens;
            boost::split(title_tokens, title, boost::is_any_of(dubious_delimiters));
        
            vector<shared_ptr<Product>> results;
            search_for_product(product_tree, title_tokens, results);

            // if we get an unambiguous result from the search, assume success
            if(results.size() == 1) {
                const auto &product = results[0];
                (*product)["listings"].append(listing_json);
            }
        }
        results_file << product_tree;
    }
}
        
int main() {

    ofstream results_file("results.txt");
    ifstream listings_file("../data/listings.txt");
    ifstream products_file("../data/products.txt");

    if(!listings_file.is_open()) {
        cout << "../data/listings.txt not found" << endl;
        return(EXIT_FAILURE);
    }
    if(!products_file.is_open()) {
        cout << "../data/products.txt not found" << endl;
        return(EXIT_FAILURE);
    }

    ProductMatchingTree::match_listings(results_file, listings_file, products_file);
    cout << "results.txt successfullly written" << endl;

    return(EXIT_SUCCESS);
}
