'use strict';

class LikeButton extends React.Component {
  constructor(props) {
    super(props);
    this.state = { liked: false };
  }

  render() {
    if (this.state.liked) {
      return this.props.name;
    }

    return React.createElement(
      'button',
      { onClick: () => this.setState({ liked: true }), className: "btn btn-primary" },
      'Like'
    );
  }
}


class external_link_image extends React.Component {
  constructor(props){
    super(props)
  }

  render(){
    const p1 = React.createElement("path", {fill_rule:"evenodd", d:"M8.636 3.5a.5.5 0 0 0-.5-.5H1.5A1.5 1.5 0 0 0 0 4.5v10A1.5 1.5 0 0 0 1.5 16h10a1.5 1.5 0 0 0 1.5-1.5V7.864a.5.5 0 0 0-1 0V14.5a.5.5 0 0 1-.5.5h-10a.5.5 0 0 1-.5-.5v-10a.5.5 0 0 1 .5-.5h6.636a.5.5 0 0 0 .5-.5z"})
    const p2 = React.createElement("path", {fill_rule:"evenodd", d:"M16 .5a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h3.793L6.146 9.146a.5.5 0 1 0 .708.708L15 1.707V5.5a.5.5 0 0 0 1 0v-5z"})

    return React.createElement("svg", {xlns:"http://www.w3.org/2000/svg", width:"10", height:"10", fill:"currentColor", class:"bi bi-box-arrow-up-right", viewBox:"0 0 16 16"},p1, p2)
  }
}


function create_many(){
  const like_btn_1 = React.createElement(LikeButton, {name:"TEST"});
  const like_btn_2 = React.createElement(LikeButton, {name: "LOL"});
  const element = React.createElement("div", null, like_btn_1, like_btn_2)
  root.render(React.createElement(external_link_image));
}

const domContainer = document.querySelector('#root');
const root = ReactDOM.createRoot(domContainer);
create_many();