<script>

        function add() {
            var sum = 0;
            var perhead = 0;
            $(".add").each(function() {
                sum += +this.value;
            });

            perhead = (sum/10).toPrecision(6);
            //return two values as an array.
            return [sum, perhead];
        }

        $('#add').click(function() {
            var total = new add() //creating array object of function add
            //retrieve value of an array of respective index
            sum = total[0];
            perhead = total[1];

            //showing those values in the html
            $('#total').html(sum);
            $('#perhead').html(perhead);

            //call function to calculate difference between per head and expenses
            difference(perhead);
            // for clearing the input box
<!--            $(".add").each(function() {-->
<!--                $('.add').val('');-->

<!--            });-->

        });

        function difference(perhead){
            var Ndata = []; // initializing new dict for negative value - less than perhead
            var Pdata = []; // initializing new dict for positive value -  more than perhead
            var Zdata = []; // initializing new dict for equal to perhead value
            $(".add").each(function() {
                var diff = (this.value-perhead).toPrecision(6);
                //console.log(this.value, this.name);
                if(diff>0){
                    Pdata.push({
                                'name': this.name,
                                'expenses': this.value,
                                'perhead': perhead,
                                'giveORreceive':diff,
                              });
                           }
                else if(diff<0){
                    Ndata.push({
                                'name': this.name,
                                'expenses': this.value,
                                'perhead': perhead,
                                'giveORreceive':diff,
                              });
                           }
                 else if(diff===0){
                    Zdata.push({
                                'name': this.name,
                                'expenses': this.value,
                                'perhead': perhead,
                                'giveORreceive':diff,
                              });
                           }
            });
//print all dict
console.log(Pdata);
console.log(Ndata);
//console.log(Zdata);

                // sort dictionary value by give or reveive amount
                // use slice() to copy the array and not just make a reference

                //sorting of Pdata
                var PdataSorted = Pdata.slice(0);
                PdataSorted.sort(function(b,a) {
                        return a.giveORreceive - b.giveORreceive;
                    });
                    console.log('Receiver data sorted by give or receive:');
                    console.log(PdataSorted);


                //sorting of Ndata
                var NdataSorted = Ndata.slice(0);
                NdataSorted.sort(function(a,b) {
                        return a.giveORreceive - b.giveORreceive;
                    });
                    console.log('Giver data sorted by give or receive:');
                    console.log(NdataSorted);

                //sorting of Zdata
                // we don't need to sort this dict because it will have all strictly zero in give or receive

                /// the calculation part is below
                ///

                var finalData = []; // initializing new dict for calculated value

                var count = 0;

                    if(count<NdataSorted.length){

                        for(j=0; j<=NdataSorted.length-1; j++){
                            console.log(count, j, 'initial', PdataSorted.length, NdataSorted)
                            if(count<PdataSorted.length){

                            toReceive = PdataSorted[count]['giveORreceive'];
                            //toReceive =tReceive;
                            console.log(toReceive, 'receiver');

                            var toGive = NdataSorted[j]['giveORreceive']; //retrieve form key of first index
                            console.log( toGive, 'giver');
                            //var receiver_Balance = +toReceive + +toGive;
                            var absGiver = Math.abs(toGive)
                            console.log(absGiver, 'abs giver value');
                            console.log(NdataSorted[j]['giveORreceive'], 'giver');

                            //checking if giver is greater than receiver in absolute value
                            if(absGiver>toReceive){


                                    var receiver_Balance = absGiver-toReceive;
                                    //adding value to dictionary
                                    finalData.push({
                                            'FromName': NdataSorted[j]['name'],
                                            'toName': PdataSorted[count]['name'],
                                            'amount': toReceive,
                                      });
                                    //receiver will be zero and giver will be absGiver-toReceive
                                    //update the both NdataSorted and PdataSorted with above value
                                    PdataSorted[count]['giveORreceive']=0;
                                    //delete PdataSorted[count];
                                    toGive = (toReceive - absGiver);
                                    console.log(toGive, 'new give');
                                    toReceive = 0;
                                    console.log(PdataSorted);
                                    console.log(finalData);
                                    count++;
                                    console.log(count, 'last');
                                    NdataSorted[j]['giveORreceive']=toGive.toPrecision(6);
                                    console.log(NdataSorted);

                                    j=j-1;
                                    console.log(j, 'j');


                            }else{
                                var dis = (+toReceive + +toGive).toPrecision(6);
                                //adding value to dictionary
                                finalData.push({
                                        'FromName': NdataSorted[j]['name'],
                                        'toName': PdataSorted[count]['name'],
                                        'amount': absGiver,
                                  });
                                  //giver will be zero and receiver will be +toReceive + +toGive
                                  //update the both NdataSorted and PdataSorted with above value

                                  toReceive = dis;
                                  console.log(toReceive, 'new rece');
                                  //delete NdataSorted[i];
                                  if(toReceive>0){
                                  console.log(j);
                                        PdataSorted[count]['giveORreceive']=dis;
                                        console.log('no property');
                                  }
                                  console.log(finalData);
                                  console.log('final Data');
                                  console.log(PdataSorted.length, NdataSorted.length, count);
                                  //printfun(finalData);
                                  console.log('final Data11');

                                  if (toReceive<=0){
                                    count++;
                                  }

                            }

                            }
}


                        }


                // print value to the div


                console.log(finalData);
                for(x=0; x<finalData.length; x++){
                    console.log(finalData[x]['amount']);
                    var msgDivTag1 = document.createElement('div');
                    var from = document.createElement('label');
                    msgDivTag1.appendChild(from);
                    from.textContent = 'From ' + finalData[x]['FromName'] + ' to ' + finalData[x]['toName'] + ' ' + finalData[x]['amount'] ;
                    document.querySelector('#cal').appendChild(msgDivTag1);
                }

                                 ///
                 ///calculation part ends

        // function ends here
        }






</script>