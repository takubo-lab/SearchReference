import * as React from "react";
import PropTypes from "prop-types";
import { DefaultButton } from "@fluentui/react";
import Header from "./Header";
import HeroList from "./HeroList";
import Progress from "./Progress";
//import './custom_button.css';

/* global Word, require */

export default class App extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      listItems: [],
      message: "",
    };
  }

  componentDidMount() {
    this.setState({
      listItems: [
        {
          icon: "Edit",
          primaryText: "Rephrased Text by ChatGPT",
        },
        
      ],
    });
  }

  rephraseChatGPT = async () => {
    this.setState({
      listItems: [],
      message: "",
    });

    Office.context.document.getSelectedDataAsync(Office.CoercionType.Text,
      (result) => {  // Changed this to an arrow function
        if (result.status === Office.AsyncResultStatus.Succeeded) {

          fetch('http://localhost:5000/process', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: result.value })
          })
          .then(response => response.json())
          .then(data => {
            var message = data.result;
            this.setState({ message });
            this.setState({
                listItems: data.map(() => ({
                  icon: "Document",
                  primaryText: ``,
                  
                })),
              }); 
          })
          .catch((error) => {
            console.error('Error:', error);
          });
        }
      }
    );
  };
  // 新しいクリックイベント
listLiterature = async () => {
  this.setState({
    listItems: [],
    message: "",
  });


  Office.context.document.getSelectedDataAsync(Office.CoercionType.Text,
    async (result) => {
      // Convert the selected text to an embedding vector using the OpenAI API
      const response = await fetch('http://localhost:5000/calculate_similarity', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: result.value })
      });

      if (!response.ok) {
        console.error("HTTP error", response.status);
        return;
      }
      
      const data = await response.json();
      
      // Update the state to reflect the top 20 similar literature
      var message = "";
      this.setState({ message });
      this.setState({
        listItems: data.map(lit => ({
          icon: "Document",
          primaryText: `${lit.title}, ${lit.secondary_title}, ${lit.year} (Score: ${lit.similarities.toFixed(2)}, PMID: <a href='https://www.ncbi.nlm.nih.gov/pubmed/${lit.accession_number}'>${lit.accession_number} </a>) \n `,
          secondaryText: `Abstract: ${lit.abstract}, PMID: ${lit.id}`,
        })),
      });
    }
  );
};

render() {
    const { title, isOfficeInitialized } = this.props;
  
    if (!isOfficeInitialized) {
      return (
        <Progress
          title={title}
          logo={require("./../../../assets/logo-filled.png")}
          message="Please sideload your addin to see app body."
        />
      );
    }
  
    return (
      <div className="ms-welcome">
        <Header logo={require("./../../../assets/logo-filled.png")} title={this.props.title} message="Welcome" />
        <HeroList message="Search and find" items={this.state.listItems}>
          <p>{this.state.message}</p>
          <p className="ms-font-l">
            <b>Ask whichever you want</b>
          </p>
          <div className="ms-welcome__button-container">
            <DefaultButton className="ms-welcome__action" iconProps={{ iconName: "ChevronRight" }} onClick={this.rephraseChatGPT}>
              Rephrase
            </DefaultButton>
            <DefaultButton className="ms-welcome__action" iconProps={{ iconName: "ChevronRight" }} onClick={this.listLiterature}>
              Search Literature
            </DefaultButton>
          </div>
        </HeroList>
      </div>
    );
  }
}
