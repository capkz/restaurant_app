// event handler for each button to update the cart information
var updateBtns =document.getElementsByClassName("update-cart")



for (var i=0; i<updateBtns.length ; i++){

	updateBtns[i].addEventListener("click",	function(){
		var productId = this.dataset.product
		var action = this.dataset.action
		console.log('productId:', productId, 'Action:', action )

		console.log('User : ', user)

		if(user== 'AnonymousUser'){
			console.log('User is not authenticated')

		}else (
			updateUserOrder(productId,action)
			  )
		}
	);

}

function updateUserOrder(productId,action){
	console.log('User is authenticated, sending data ..')

		var url='/update_item/' //sends data to the view

		fetch(url, {  //to send our POST data 
			method: 'POST', //POST data : when clicked , when data is received
			headers:{
				'Content-Type':'application/json',
				'X-CSRFToken': csrftoken,
			},
			body: JSON.stringify({'productId': productId,'action': action}) //the data to be sent to the backend as object
		})

		.then((response) => { //response to get when data is sent
			return response.json();
		})
		
		.then((data) => {
			console.log('data : ', data)
			location.reload() //reload the page
		});
}