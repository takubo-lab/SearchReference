import * as React from "react";
import PropTypes from "prop-types";

export default class HeroList extends React.Component {
  render() {
    const { children, items, message } = this.props;

const listItems = items.map((item, index) => (
    <li className="ms-ListItem" key={index}>
        <i className={`ms-Icon ms-Icon--${item.icon}`}></i>
        <span 
            className="ms-font-m ms-fontColor-neutralPrimary"
            /* changed here*/
            dangerouslySetInnerHTML={{ __html: item.primaryText }} 
        />
    </li>
));
//<h2 className="ms-font-xl ms-fontWeight-semilight ms-fontColor-neutralPrimary ms-u-slideUpIn20">{message}</h2>
    return (
      <div className="ms-welcome__main">
        <ul className="ms-List ms-welcome__features ms-u-slideUpIn10">{listItems}</ul>
        {children}
      </div>
    );
  }
}

HeroList.propTypes = {
  children: PropTypes.node,
  items: PropTypes.array,
  message: PropTypes.string,
};
